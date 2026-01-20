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
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from dotenv import load_dotenv

from database import get_session, get_user_by_id
from models import User

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

# Security scheme
security = HTTPBearer()

def create_access_token(user_id: int) -> str:
    """Create a JWT access token for a user."""
    expire = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[int]:
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None

def decode_google_token(credential: str) -> dict:
    """
    Decode a Google OAuth credential token.
    Note: This is a basic decode without verification.
    For production, consider using google-auth library for full verification.
    """
    try:
        # Google credential is a JWT, we decode the payload
        # The token has 3 parts: header.payload.signature
        import base64
        import json

        parts = credential.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        # Decode the payload (middle part)
        # Add padding if needed
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_payload = json.loads(decoded_bytes)

        return {
            "sub": decoded_payload.get("sub"),  # Google's unique user ID
            "email": decoded_payload.get("email"),
            "name": decoded_payload.get("name"),
            "picture": decoded_payload.get("picture")
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Google token: {str(e)}")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise credentials_exception

    user = get_user_by_id(session, user_id)
    if user is None:
        raise credentials_exception

    return user
