from pydantic import BaseModel

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



