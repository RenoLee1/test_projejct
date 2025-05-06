from typing import Optional
from sqlmodel import Session, select
from app.models.user import User

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    statement = select(User).where(User.username == username)
    return db.scalar(statement)

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by id"""
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)

def update_user(db: Session, user: User) -> User:
    """Update user information"""
    db.add(user)
    db.commit()
    db.refresh(user)
    return user