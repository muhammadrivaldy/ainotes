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

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from models import ChatRequest, ChatResponse, ChatMessage, Message
from database import create_db_and_tables, get_session
from brain import brain
import uvicorn
import os

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

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"status": "Second Brain is active"}

@app.get("/history", response_model=List[ChatMessage])
def get_history(session: Session = Depends(get_session)):
    messages = session.exec(select(ChatMessage).order_by(ChatMessage.timestamp)).all()
    return messages

@app.delete("/history")
def clear_history(session: Session = Depends(get_session)):
    messages = session.exec(select(ChatMessage)).all()
    for message in messages:
        session.delete(message)
    session.commit()
    return {"status": "History cleared"}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, body: ChatRequest, session: Session = Depends(get_session)):
    try:
        # 1. Save User Message to DB
        user_msg = ChatMessage(role="user", content=body.message)
        session.add(user_msg)
        session.commit()
        session.refresh(user_msg)

        # 2. Retrieve History from DB for context
        # Fetch all or last N messages to establish context
        history_records = session.exec(select(ChatMessage).order_by(ChatMessage.timestamp)).all()
        
        # Convert DB records to the format Brain expects (List[Message] or similar dict)
        # Brain expects objects with .role and .content attributes
        brain_history = [Message(role=msg.role, content=msg.content) for msg in history_records]

        # 3. Process with Brain
        # Note: We pass the history we just fetched from DB
        response_text = brain.process_message(body.message, brain_history)

        # 4. Save AI Response to DB
        ai_msg = ChatMessage(role="assistant", content=response_text)
        session.add(ai_msg)
        session.commit()

        return ChatResponse(response=response_text)
    except Exception as e:
        # Log the error internally
        print(f"Error processing chat: {e}")
        # Return generic error to user to avoid leaking details
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
