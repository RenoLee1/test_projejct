from typing import Literal, Optional
from pydantic import BaseModel, Field

class UserApprovalUpdate(BaseModel):
    user_id: int
    status: Optional[Literal["approved", "rejected"]]
    reviewer: Optional[str]
    version: Optional[int]
    username: Optional[str] = Field(default=None)


class UserWithApproval(BaseModel):
    user_id: int
    username: str
    reviewer: Optional[str]
    status: Optional[str]

class UserApprovalRead(BaseModel):
    user_id: int
    username: Optional[str]
    status: str
    reviewer: Optional[str]
    version: int

    class Config:
        from_attributes = True
class UserWithApprovalRead(BaseModel):
    first_name: str
    last_name: str
    email: str
    affiliation: str
    research: Optional[str]
    role: str
    status: str
    version: int
    user_id: int
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True

class RejectUserRequest(BaseModel):
    user_id: int
    comment:Optional[str]
    is_cancel: bool = False
    version: int
