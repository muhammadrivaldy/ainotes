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

from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List, Optional
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

# Maximum file size for PDF uploads (50MB by default, configurable via environment)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))  # bytes

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

def is_valid_pdf(file_path: str) -> bool:
    """Validate that a file is a valid PDF by checking for PDF magic bytes."""
    try:
        with open(file_path, "rb") as f:
            # Read first 5 bytes to check for PDF signature
            header = f.read(5)
            # PDF files start with %PDF- (e.g., %PDF-1.4, %PDF-1.7)
            return header.startswith(b'%PDF-')
    except (IOError, OSError) as e:
        logger.error(f"Error validating PDF file {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating PDF file {file_path}: {e}")
        return False

@app.post("/documents/upload", response_model=DocumentUploadResponse, deprecated=True)
@limiter.limit("5/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    [DEPRECATED] Upload a PDF document and index it into the knowledge base.
    Use /chat endpoint with file attachment instead for context-aware processing.
    """
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
        # Read and write file in chunks while validating size
        bytes_read = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        size_exceeded = False
        
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                
                # Check size before writing to prevent any excess data
                if bytes_read + len(chunk) > MAX_UPLOAD_SIZE:
                    size_exceeded = True
                    break
                
                f.write(chunk)
                bytes_read += len(chunk)
        
        # If file size exceeded, clean up and raise error
        if size_exceeded:
            os.remove(file_path)
            max_size_mb = MAX_UPLOAD_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {max_size_mb:.0f}MB"
            )

        # Validate that the uploaded file is actually a PDF
        if not is_valid_pdf(file_path):
            # Clean up invalid file
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to remove invalid PDF file {file_path}: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. The file does not contain valid PDF content."
            )

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
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Process a chat message for the authenticated user, with optional file attachment."""
    file_path = None
    file_saved = False
    
    try:
        # Handle file if provided
        pdf_context = None
        if file:
            if not file.filename or not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are supported")
            
            # Create user-specific upload directory
            user_upload_dir = os.path.join(UPLOADS_DIR, str(current_user.id))
            os.makedirs(user_upload_dir, exist_ok=True)

            # Save file temporarily
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            original_filename = os.path.basename(file.filename)
            sanitized_filename = re.sub(r'[^A-Za-z0-9._-]', '_', original_filename)
            safe_filename = f"{timestamp}_{sanitized_filename}"
            file_path = os.path.join(user_upload_dir, safe_filename)

            # Read and write file in chunks with size validation
            bytes_read = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            size_exceeded = False
            
            with open(file_path, "wb") as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    
                    if bytes_read + len(chunk) > MAX_UPLOAD_SIZE:
                        size_exceeded = True
                        break
                    
                    f.write(chunk)
                    bytes_read += len(chunk)
            
            if size_exceeded:
                os.remove(file_path)
                max_size_mb = MAX_UPLOAD_SIZE / (1024 * 1024)
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds maximum allowed size of {max_size_mb:.0f}MB"
                )

            # Validate PDF
            if not is_valid_pdf(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to remove invalid PDF file {file_path}: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF file. The file does not contain valid PDF content."
                )

            # Extract PDF text for context
            user_brain = get_user_brain(current_user.id)
            pdf_data = user_brain.extract_pdf_text(file_path)
            
            if "error" in pdf_data:
                raise HTTPException(status_code=400, detail=pdf_data["error"])
            
            pdf_context = f"\n\n[ATTACHED DOCUMENT: {pdf_data['filename']} ({pdf_data['page_count']} pages)]\n{pdf_data['preview']}\n[END OF DOCUMENT PREVIEW]"

        # Detect save intent from message
        save_keywords = [
            "save", "index", "add to knowledge", "remember this document",
            "store", "keep", "add this", "save this"
        ]
        should_save = any(keyword in message.lower() for keyword in save_keywords)

        # If user wants to save, process the document first
        save_result = None
        if file and should_save and file_path:
            user_brain = get_user_brain(current_user.id)
            add_doc_tool = next((t for t in user_brain.tools if t.name == "add_document"), None)
            if add_doc_tool:
                save_result = add_doc_tool.func(file_path=file_path)
                file_saved = True

        # 1. Save User Message to DB (original message without PDF context)
        user_msg = ChatMessage(
            user_id=current_user.id,
            role="user",
            content=message,
            attachment_name=file.filename if file else None
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
        
        # Pass PDF context to process_message if file was provided but not saved
        if file and pdf_context and not should_save:
            # Extract PDF data for passing to brain
            pdf_data = user_brain.extract_pdf_text(file_path)
            response_text = user_brain.process_message(message, brain_history, pdf_context=pdf_data)
        elif file and should_save and save_result:
            # If saved, let user know and process message normally
            response_text = f"{save_result}\n\nHow can I help you with this document?"
        else:
            # Normal message processing without file
            response_text = user_brain.process_message(message, brain_history)

        # 4. Save AI Response to DB
        ai_msg = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=response_text
        )
        session.add(ai_msg)
        session.commit()

        return ChatResponse(response=response_text, suggestions=[])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")
    finally:
        # Clean up temporary file if not saved to knowledge base
        if file_path and not file_saved and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to cleanup temporary file {file_path}: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
