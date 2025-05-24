from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)  # Auto-incremented feedback ID
    username: str = Field(max_length=50, description="User-entered name or handle")  # Username label (not FK)
    email: str = Field(max_length=255, description="User's email address")  # Email field
    category: str = Field(max_length=255, description="Feedback category or type")  # e.g., bug, request
    message: str = Field(description="Feedback message")  # Full message text
    created_time: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")  # Auto-filled
    status: str = Field(max_length=50, description="Processing status")  # e.g., read/unread, resolved

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")  # FK to User

    # Relationships
    user: Optional["User"] = Relationship()
