from typing import Optional
from datetime import datetime
from sqlmodel import Session
from app.models.user import User
from app.utils.auth_util import verify_password
from app.crud.user_crud import get_user_by_username, update_user,get_user_by_email,create_user
from fastapi import HTTPException
from app.schemas.user_schema import UserRegister
import smtplib
from email.message import EmailMessage
import logging
logger = logging.getLogger(__name__)
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

def register_user(db: Session, register_data: UserRegister) -> None:
    if get_user_by_email(db, register_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(db, register_data.username):
        raise HTTPException(status_code=400, detail="username already registered")
    create_user(
        db=db,
        username=register_data.username,
        password=register_data.password,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        email=register_data.email,
        country=register_data.country,
        affiliation=register_data.affiliation,
        research=register_data.research,
    )
    send_admin_notification(register_data.email, register_data.username)

def send_admin_notification(user_email: str, username: str):
    admin_email = "ZHENGXIY@student.unimelb.edu.au"
    #sender email
    sender_email = "378868084@qq.com"
     #smtp 授权码
    sender_password = "jfsxoomrobfrbigb"

    msg = EmailMessage()
    msg["Subject"] = "【new user register !】"
    msg["From"] = sender_email
    msg["To"] = admin_email
    msg.set_content(f"Users requiring your approval：\nusername：{username}\nemail：{user_email}")

    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as smtp:
            smtp.set_debuglevel(1)
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            logger.info("Email successfully sent to admin.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")