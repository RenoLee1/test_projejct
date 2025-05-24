from fastapi import HTTPException, Request, Depends
from sqlmodel import Session
from app.database.session import get_session
from app.crud.user_crud import get_user_by_id
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify password (password is not encrypted yet for convenience)"""
    # return pwd_context.verify(plain_password, hashed_password)
    if plain_password != hashed_password:
        return False
    else:
        return True

def get_password_hash(password: str) -> str:
    """Get password hash"""
    return pwd_context.hash(password)

async def get_current_user(request: Request, db: Session = Depends(get_session)):
    """
    Get current user from session
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user