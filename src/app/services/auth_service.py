from typing import Optional
from datetime import datetime
from sqlmodel import Session
from app.models.user import User
from app.utils.auth_util import verify_password
from app.crud.user_crud import get_user_by_username, update_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """use authentication"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def update_user_login_info(db: Session, user: User, ip: str) -> User:
    """update login time and ip"""
    user.login_time = datetime.now()
    user.login_ip = ip
    return update_user(db, user) 