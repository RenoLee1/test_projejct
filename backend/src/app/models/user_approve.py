from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class UserApproval(SQLModel, table=True):
    __tablename__ = "user_approval"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="user.id", unique=True)
    username: str = Field(max_length=50, foreign_key="user.username", description="FK to user.username")
    status: str = Field(default="pending", max_length=20, description="Approval status")
    reviewer: Optional[str] = Field(default=None, max_length=50, description="Reviewer name")
    version: int = Field(description="Approval request version")
    register_time: Optional[datetime] = Field(default=None, description="Request submission time")
    process_time: Optional[datetime] = Field(default=None, description="Request processing time")

    # ✅ Add this field:
    rejection_reason: Optional[str] = Field(default=None, max_length=255, description="Reason for rejection")

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="approval",
        sa_relationship_kwargs={"foreign_keys": "UserApproval.user_id", "uselist": False}
    )

    user_by_username: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "UserApproval.username"}
    )
