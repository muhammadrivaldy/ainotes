# AI Notes API
# Copyright (C) 2026 Rivaldy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from models import (
    ChatRequest, ChatResponse, ChatMessage, Message,
    GoogleAuthRequest, AuthResponse, UserResponse, User, Suggestion,
    Tag, TaggedItem, DocumentUploadResponse
)
from database import create_db_and_tables, get_session, get_or_create_user
from auth import create_access_token, decode_google_token, get_current_user
from brain import SecondBrain, UPLOADS_DIR
import uvicorn

logger = logging.getLogger(__name__)

# Setup Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Second Brain AI API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
    "*"  # Allow all for dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store user-specific brain instances
user_brains: dict[int, SecondBrain] = {}

def get_user_brain(user_id: int) -> SecondBrain:
    """Get or create a SecondBrain instance for a specific user."""
    if user_id not in user_brains:
        user_brains[user_id] = SecondBrain(user_id=user_id)
    return user_brains[user_id]

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"status": "Second Brain is active"}

# --- Auth Endpoints ---
@app.post("/auth/google", response_model=AuthResponse)
def google_auth(body: GoogleAuthRequest, session: Session = Depends(get_session)):
    """Authenticate with Google OAuth and return a JWT token."""
    try:
        # Decode Google token to get user info
        google_data = decode_google_token(body.credential)

        if not google_data.get("sub"):
            raise HTTPException(status_code=400, detail="Invalid Google token")

        # Get or create user in database
        user = get_or_create_user(
            session=session,
            google_id=google_data["sub"],
            email=google_data.get("email", ""),
            name=google_data.get("name", ""),
            picture=google_data.get("picture")
        )

        # Create JWT token
        access_token = create_access_token(user.id)

        return AuthResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "google_id": user.google_id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in Google auth: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user

# --- Chat Endpoints (Protected) ---
@app.get("/history", response_model=List[ChatMessage])
def get_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get chat history for the authenticated user."""
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.timestamp)
    ).all()
    return messages

@app.delete("/history")
def clear_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Clear chat history for the authenticated user."""
    messages = session.exec(
        select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    ).all()
    for message in messages:
        session.delete(message)
    session.commit()
    return {"status": "History cleared"}

@app.get("/tags", response_model=List[Tag])
async def get_user_tags(
    current_user: User = Depends(get_current_user)
):
    """Get all tags for current user with document counts."""
    user_brain = get_user_brain(current_user.id)
    tags = user_brain.get_all_tags()
    return tags

@app.get("/tags/{tag}/items", response_model=List[TaggedItem])
async def get_items_by_tag(
    tag: str,
    current_user: User = Depends(get_current_user)
):
    """Get all information items with a specific tag."""
    user_brain = get_user_brain(current_user.id)
    items = user_brain.get_items_by_tag(tag)
    return items

@app.post("/tags/regenerate")
async def regenerate_tags(
    current_user: User = Depends(get_current_user)
):
    """Regenerate tags for all existing information without tags."""
    user_brain = get_user_brain(current_user.id)
    count = user_brain.regenerate_all_tags()
    return {"message": f"Regenerated tags for {count} items", "count": count}

@app.post("/documents/upload", response_model=DocumentUploadResponse)
@limiter.limit("5/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF document and index it into the knowledge base."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = None  # Initialize to prevent NameError in exception handler
    
    # Create user-specific upload directory
    user_upload_dir = os.path.join(UPLOADS_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)

    # Save with timestamp prefix to avoid collisions
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    # Sanitize the original filename to prevent path traversal and invalid characters
    original_filename = os.path.basename(file.filename)
    sanitized_filename = re.sub(r'[^A-Za-z0-9._-]', '_', original_filename)
    safe_filename = f"{timestamp}_{sanitized_filename}"
    file_path = os.path.join(user_upload_dir, safe_filename)

    try:
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Process with brain's add_document tool
        user_brain = get_user_brain(current_user.id)

        # Call the add_document tool function directly
        add_doc_tool = next((t for t in user_brain.tools if t.name == "add_document"), None)
        if not add_doc_tool:
            raise HTTPException(status_code=500, detail="Document processing tool not available")

        result = add_doc_tool.func(file_path=file_path)

        # Parse chunks_added from result
        chunks_added = 0
        if "chunks added" in result:
            match = re.search(r'(\d+) chunks added', result)
            if match:
                chunks_added = int(match.group(1))

        return DocumentUploadResponse(
            message=result,
            filename=file.filename,
            chunks_added=chunks_added
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        # Clean up partial file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail="Failed to process document. Please try again later."
        )

@app.post("/knowledge/migrate")
async def migrate_knowledge(
    current_user: User = Depends(get_current_user)
):
    """Migrate legacy metadata to the new knowledge schema. Safe to run multiple times."""
    user_brain = get_user_brain(current_user.id)
    stats = user_brain.migrate_legacy_metadata()
    return {
        "message": f"Migration complete: {stats['migrated']} items migrated",
        "stats": stats
    }

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat_endpoint(
    request: Request,
    body: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Process a chat message for the authenticated user."""
    try:
        # 1. Save User Message to DB
        user_msg = ChatMessage(
            user_id=current_user.id,
            role="user",
            content=body.message
        )
        session.add(user_msg)
        session.commit()
        session.refresh(user_msg)

        # 2. Retrieve History from DB for context (user-specific)
        history_records = session.exec(
            select(ChatMessage)
            .where(ChatMessage.user_id == current_user.id)
            .order_by(ChatMessage.timestamp)
        ).all()

        # Convert DB records to the format Brain expects
        brain_history = [Message(role=msg.role, content=msg.content) for msg in history_records]

        # 3. Process with user-specific Brain
        user_brain = get_user_brain(current_user.id)
        response_text = user_brain.process_message(body.message, brain_history)

        # 4. Save AI Response to DB
        ai_msg = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=response_text
        )
        session.add(ai_msg)
        session.commit()

        return ChatResponse(response=response_text, suggestions=[])
    except Exception as e:
        print(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
