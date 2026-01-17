from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import List, Optional
from datetime import datetime

# --- Database Models ---
class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- API Request/Response Models ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    # We make history optional since the backend will now track it,
    # but we keep it for backward compatibility or context injection.
    history: List[Message] = [] 

class ChatResponse(BaseModel):
    response: str
