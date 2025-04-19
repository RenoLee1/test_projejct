from typing import Optional
from sqlmodel import Session, select
from app.models.user import User


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
        role=role,
        login_time=None,
        login_ip=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
