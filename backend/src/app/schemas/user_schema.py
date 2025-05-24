from pydantic import BaseModel, EmailStr, Field
from typing import Optional
# Login request
class UserLogin(BaseModel):
    username: str
    password: str

# User information
class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    role: str | None = None

    model_config = {
        "from_attributes": True
    }

class UserRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    country: str
    affiliation: str
    research: str



