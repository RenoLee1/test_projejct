from fastapi import Depends, HTTPException, Request, status,APIRouter
from sqlmodel import Session
from typing import Optional
from app.schemas.response import success
from app.schemas.user_schema import UserInfo
from app.crud.user_crud import get_user_by_id
from app.schemas.response import Response
from app.database.session import get_session

def get_current_user(
    request: Request,
    db: Session = Depends(get_session)
) -> UserInfo:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in",
            headers={"WWW-Authenticate": "Session"},
        )
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # convert ORM User to UserInfo Pydantic model
    return UserInfo.from_orm(user)


from app.database.session import get_session
from app.models.user import User

async def get_current_user_id(request: Request) -> int:
    """
    Get the current user's ID from the session
    Raise HTTPException if user is not logged in
    """
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in",
            headers={"WWW-Authenticate": "Session"},
        )
    return request.session["user_id"]

async def verify_admin_access(request: Request) -> int:
    """
    Verify that the current user has admin role
    Returns user_id if verified, otherwise raises HTTPException
    """
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in",
            headers={"WWW-Authenticate": "Session"},
        )
    
    if "role" not in request.session or request.session["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return request.session["user_id"]
