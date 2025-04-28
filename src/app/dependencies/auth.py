from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session
from typing import Optional

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
