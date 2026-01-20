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
from sqlmodel import SQLModel, create_engine, Session, select
from models import User

# Database path - now in database/ folder
DATABASE_DIR = os.path.join(os.path.dirname(__file__), "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

sqlite_file_name = os.path.join(DATABASE_DIR, "chat_history.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- User Functions ---
def get_user_by_google_id(session: Session, google_id: str) -> User | None:
    """Get a user by their Google ID."""
    statement = select(User).where(User.google_id == google_id)
    return session.exec(statement).first()

def create_user(session: Session, google_id: str, email: str, name: str, picture: str | None = None) -> User:
    """Create a new user."""
    user = User(
        google_id=google_id,
        email=email,
        name=name,
        picture=picture
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_or_create_user(session: Session, google_id: str, email: str, name: str, picture: str | None = None) -> User:
    """Get an existing user or create a new one."""
    user = get_user_by_google_id(session, google_id)
    if user:
        # Update user info in case it changed
        user.email = email
        user.name = name
        user.picture = picture
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    return create_user(session, google_id, email, name, picture)

def get_user_by_id(session: Session, user_id: int) -> User | None:
    """Get a user by their ID."""
    return session.get(User, user_id)
