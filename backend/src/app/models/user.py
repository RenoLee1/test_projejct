from typing import Optional, List
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship

# user table
class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False, description="User ID")  # Auto-incremented primary key
    username: str = Field(nullable=False, max_length=50, unique=True, description="Username")  # Unique username
    password: str = Field(nullable=False, max_length=255, description="Password hash")  # Hashed password
    first_name: str = Field(nullable=False, max_length=255, description="First name")  # Required first name
    last_name: str = Field(nullable=False, max_length=255, description="Last name")  # Required last name
    email: str = Field(nullable=False, max_length=255, unique=True, description="Email address")  # Unique email
    role: str = Field(nullable=False, max_length=50, description="role: admin/user")  # Role (e.g., admin/user)
    status: str = Field(nullable=False, max_length=50, description="Account status (e.g., active/pending)")  # Account status (e.g., active/pending)
    affiliation: str = Field(nullable=False, max_length=255, description="Organization")  # Organization or institution
    research: str = Field(nullable=False, max_length=255, description="Research description")   # Research description
    country: str = Field(nullable=False, max_length=50, description="User Country")  # Country field
    session_id: Optional[int] = Field(default=None, foreign_key="session.id", unique=True, description="Reference to session")  # Optional FK to sessions

    # Relationships (only those supported by the updated design)
    approval: Optional["UserApproval"] = Relationship(back_populates="user", sa_relationship_kwargs={"foreign_keys": "UserApproval.user_id", "uselist": False}) # 1 to 1
    jobs: List["Job"] = Relationship(back_populates="user")  # One-to-many: user → jobs
    session: Optional["Session"] = Relationship(back_populates="user", sa_relationship_kwargs={"foreign_keys": "User.session_id"}) # Optional link to session (one-to-one)
