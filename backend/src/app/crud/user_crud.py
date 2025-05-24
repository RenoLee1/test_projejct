from typing import Optional
from sqlmodel import Session, select
from app.models.user import User
from app.models.user_approve import UserApproval
from datetime import datetime
from zoneinfo import ZoneInfo

# use username to find user
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username.strip())
    return db.exec(statement).first()


# use id to find user
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    statement = select(User).where(User.id == user_id)
    return db.exec(statement).first()


# use email to find user
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email.ilike(email.strip()))
    return db.exec(statement).first()


# def get_user_by_username_or_email(db: Session, username: str, email: str) -> Optional[User]:
def update_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_approve_by_id(db: Session, user_id: int) -> Optional[UserApproval]:
    statement = select(UserApproval).where(UserApproval.user_id == user_id)
    return db.exec(statement).first()

def create_user_approval(
    db: Session,
    user_id: int,
    status: str,
    username: str,
    reviewer: str = None,
    version: int = 1
) -> UserApproval:
    melbourne_time = datetime.now(ZoneInfo("Australia/Melbourne"))

    approval = UserApproval(
        user_id=user_id,
        status=status,
        reviewer=reviewer,
        version=version,
        username=username,
        register_time=melbourne_time,
        process_time=melbourne_time
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval

# create a new user
def create_user(
    db: Session,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
    country: str,
    affiliation: str,
    status: str = "active",
    role: str = "user",
    research: Optional[str] = None,
) -> User:
    user = User(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        country=country,
        affiliation=affiliation,
        research=research,
        status=status,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_id(db: Session, user_id: int) -> None:
    db.query(User).filter(User.id == user_id).delete()
    db.commit()

def delete_user_approval_by_user_id(db: Session, user_id: int) -> None:
    db.query(UserApproval).filter(UserApproval.user_id == user_id).delete()
    db.commit()

def promote_user_to_admin(db: Session, user_id: int) -> bool:
    affected = db.query(User).filter(User.id == user_id).update({"role": "admin"})
    db.commit()
    return affected == 1

def get_approval_by_user_id(db: Session, user_id: int) -> UserApproval:
    return db.query(UserApproval).filter(UserApproval.user_id == user_id).first()

def update_approval_by_user_id_approve(db: Session, user_id: int) -> bool:
    tx = db.query(UserApproval).filter(UserApproval.user_id == user_id).update({"status": "approved"})
    db.commit()
    return tx == 1