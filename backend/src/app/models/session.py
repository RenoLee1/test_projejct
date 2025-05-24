from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Session(SQLModel, table=True):
    __tablename__ = "session"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    login_time: datetime = Field(description="Time of login")
    login_ip: Optional[str] = Field(default=None, max_length=45, description="IP address used for login")
    expiration: Optional[datetime] = Field(default=None, description="Session expiration time")

    # Relationships
    user: Optional["User"] = Relationship(back_populates="session", sa_relationship_kwargs={"foreign_keys": "User.session_id", "uselist": False}
    )

