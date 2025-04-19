from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.database.session import get_session
from app.schemas.user_schema import UserLogin, UserInfo,UserRegister
from app.services.auth_service import authenticate_user, update_user_login_info,register_user
from app.schemas.response import success, error, Response

router = APIRouter(prefix="/api/auth", tags=["auth"])

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

@router.post("/register", response_model=Response[UserRegister])
def register(
        register_data: UserRegister,
        db: Session = Depends(get_session)
):
    """
    Register a new user account
    """
    # 1. Check if email or username already exists
    register_user(db, register_data)

    return success(message="Registration successful")