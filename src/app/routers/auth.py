from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.database.session import get_session
from app.schemas.user_schema import UserLogin, UserInfo
from app.services.auth_service import authenticate_user, update_user_login_info
from app.schemas.response import success, error, Response

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Response[UserInfo])
def login(
        request: Request,
        login_data: UserLogin,
        db: Session = Depends(get_session)
):
    """
    User login, store user info in session
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        return error(code=401, message="Invalid username or password")

    # Update login information
    client_ip = request.client.host
    user = update_user_login_info(db, user, client_ip)

    # Store user info in session
    request.session["user_id"] = user.id
    request.session["role"] = user.role

    return success(data=UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    ))

@router.post("/logout")
def logout(request: Request):
    """
    User logout
    """
    request.session.clear()
    return success(message="Logged out successfully")
