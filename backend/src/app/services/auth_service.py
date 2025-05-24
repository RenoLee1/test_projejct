from typing import Optional
from datetime import datetime
from sqlmodel import Session, select
from app.models.user import User
from app.models.user_approve import UserApproval
from app.models.session import Session as SessionTable
from app.utils.auth_util import verify_password

from app.crud.user_crud import (
    get_user_by_username, update_user, get_user_by_email, create_user,
    get_user_approve_by_id, create_user_approval, delete_user_by_id,
    delete_user_approval_by_user_id, promote_user_to_admin,
    get_approval_by_user_id, get_user_by_id, update_approval_by_user_id_approve
)
from app.crud.user_approve_crud import (
    update_user_approval_with_version, get_all_approvals,
    update_user_approval_with_version_reject
)

from fastapi import HTTPException
from app.schemas.user_schema import UserRegister
from app.schemas.user_approve_schema import UserApprovalUpdate
import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)
def authenticate_user(db: Session, username: str, password: str) -> tuple[Optional[User], Optional[str]]:
    """
    Authenticate user and return tuple of (user, error_message)
    If authentication successful, returns (user, None)
    If authentication fails, returns (None, error_message)
    """
    user = get_user_by_username(db, username)
    if not user:
        return None, "Invalid username or password"
    
    if not verify_password(password, user.password):
        return None, "Invalid username or password"
    
    # Check user approval status
    approval = get_approval_by_user_id(db, user.id)
    if not approval or approval.status != "approved":
        return None, "Your account has not been approved yet"
        
    return user, None

def update_or_create_user_session_login_info(db: Session, user: User, ip: str) -> SessionTable:
    """Update login timestamp and IP address"""
    statement = select(SessionTable).where(
        SessionTable.user_id == user.id
    )    
    session = db.exec(statement).first()

    if not session:
        session = SessionTable(
            user_id=user.id,
            login_time=datetime.now(),
            login_ip=ip
        )
    else:
        setattr(session, "login_time", datetime.now())
        setattr(session, "login_ip", ip)
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def register_user(db: Session, register_data: UserRegister) -> int:
    existing_user = get_user_by_email(db, register_data.email)
    
    existing_username_user = get_user_by_username(db, register_data.username)
    if existing_username_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # If user exists
    if existing_user:
        approval = get_approval_by_user_id(db, existing_user.id)

        # ❌ If status is not rejected → block registration
        if approval:
            if approval.status != "rejected":
                raise HTTPException(status_code=400, detail="Email already registered")

            # ✅ Re-register allowed
            existing_user.username = register_data.username
            existing_user.password = register_data.password
            existing_user.first_name = register_data.first_name
            existing_user.last_name = register_data.last_name
            existing_user.affiliation = register_data.affiliation
            existing_user.research = register_data.research
            existing_user.status = "re-registered"
            existing_user.role = "user"

            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)

            approval.status = "re-registered"
            approval.username = register_data.username
            approval.reviewer = "Admin"
            approval.version += 1
            approval.register_time = datetime.now()
            approval.process_time = datetime.now()
            db.add(approval)
            db.commit()

            send_admin_notification(existing_user.email, existing_user.username)
            return

        # Edge case: user exists but no approval record → block
        raise HTTPException(status_code=400, detail="Email already registered")

    # ✅ New user registration
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
    user = get_user_by_username(db, register_data.username)
    if not user:
        raise HTTPException(status_code=500, detail="User registration failed")

    create_user_approval(
        db=db,
        user_id=user.id,
        username=user.username,
        status="pending",
        reviewer=None,
        version=1
    )
    send_admin_notification(user.email, user.username)
    return user.id



def send_admin_notification(user_email: str, username: str):
    admin_email = "ZHENGXIY@student.unimelb.edu.au"
    sender_email = "378868084@qq.com"
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


def approve_user(db: Session, approval_data: UserApprovalUpdate) -> None:
    success = update_user_approval_with_version(
        db=db,
        user_id=approval_data.user_id,
        status="approved",
        reviewer=approval_data.reviewer,
        current_version=approval_data.version
    )
    if not success:
        raise ValueError("Approval failed due to version conflict. Please refresh and try again.")


def reject_user(db: Session, user_id: int, version: int, comment: str, is_cancel: bool) -> None:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    # Optional: only send email if not cancelling
    if not is_cancel:
        send_rejection_email_to_user(user.email, user.username, comment)

    # Update approval status using external function (version check included)
    update_user_approval_with_version_reject(
        db=db,
        user_id=user_id,
        status="rejected",
        current_version=version,
        comment=comment
    )



def send_rejection_email_to_user(user_email: str, username: str, comment: str):
    sender_email = "378868084@qq.com"
    sender_password = "jfsxoomrobfrbigb"

    msg = EmailMessage()
    msg["Subject"] = "【register fail】"
    msg["From"] = sender_email
    msg["To"] = user_email
    msg.set_content(
        f"Dear {username},\n\n"
        f"We regret to inform you that your registration request has been rejected.\n\n"
        f"Reason: {comment}\n\n"
        f"If you have any questions or believe this was a mistake, please feel free to contact the administrator.\n\n"
        f"Best regards,\n"
        f"The Admin Team"
    )

    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            logger.info("Rejection email successfully sent to user.")
    except Exception as e:
        logger.error(f"Failed to send rejection email to user: {e}")


def read_user_approval(db: Session, user_id: int) -> Optional[UserApproval]:
    return get_user_approve_by_id(db, user_id)


def list_all_approvals(db: Session):
    return get_all_approvals(db)


def make_user_admin(db: Session, user_id: int) -> None:
    success = promote_user_to_admin(db, user_id)
    if not success:
        raise ValueError(f"User with id {user_id} not found or update failed")


def fetch_user_approval_status(db: Session, user_id: int) -> str:
    approval = get_approval_by_user_id(db, user_id)
    if not approval:
        raise ValueError("Approval record not found")
    return approval.status
