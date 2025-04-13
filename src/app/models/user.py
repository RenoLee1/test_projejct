from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel

# user table
class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False, description="User ID")
    username: str = Field(nullable=False, max_length=50, unique=True, description="Username")
    password: str = Field(nullable=False, max_length=255, description="Password hash")
    first_name: str = Field(nullable=False, max_length=255, description="First name")
    last_name: str = Field(nullable=False, max_length=255, description="Last name")
    email: str = Field(nullable=False, max_length=255, description="Email address")
    affiliation: str = Field(nullable=False, max_length=255, description="Organization")
    research: Optional[str] = Field(default=None, description="Research description")
    status: str = Field(nullable=False, max_length=50, description="Account status")
    role: Optional[str] = Field(default=None, max_length=50, description="role: admin/user")
    login_time: Optional[datetime] = Field(default=None, description="Last login time")
    login_ip: Optional[str] = Field(default=None, max_length=45, description="Last login IP address")
