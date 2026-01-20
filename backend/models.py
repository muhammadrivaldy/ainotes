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

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

# --- Database Models ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(unique=True, index=True)  # Google's 'sub' claim
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to chat messages
    messages: List["ChatMessage"] = Relationship(back_populates="user")

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="messages")

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

# --- Auth Models ---
class GoogleAuthRequest(BaseModel):
    credential: str  # Google OAuth credential token

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime
