from sqlalchemy.orm import Session
from app.models.user_approve import UserApproval
from app.models.user import User

from sqlalchemy import select
from zoneinfo import ZoneInfo
from datetime import datetime

def update_user_approval_with_version(
    db: Session,
    user_id: int,
    status: str,
    reviewer: str,
    current_version: int
) -> bool:
    melbourne_time = datetime.now(ZoneInfo("Australia/Melbourne"))

    result = db.query(UserApproval).filter(
        UserApproval.user_id == user_id,
        UserApproval.version == current_version
    ).update({
        UserApproval.status: status,
        UserApproval.reviewer: reviewer,
        UserApproval.version: UserApproval.version + 1,
        UserApproval.process_time: melbourne_time
    })

    db.commit()
    return result == 1

def get_all_approvals(db: Session):
    statement = (
        select(
            User.first_name.label("first_name"),
            User.last_name.label("last_name"),
            User.email.label("email"),
            User.affiliation.label("affiliation"),
            User.research.label("research"),
            User.role.label("role"),
            UserApproval.status.label("status"),
            UserApproval.user_id.label("user_id"),
            UserApproval.version.label("version"),
            UserApproval.rejection_reason.label("rejection_reason")
        )
        .join(UserApproval, User.id == UserApproval.user_id)
    )
    results = db.exec(statement).mappings().all()
    return results

def update_user_approval_with_version_reject(
    db: Session,
    user_id: int,
    comment: str,
    status: str,
    current_version: int
) -> bool:
    melbourne_time = datetime.now(ZoneInfo("Australia/Melbourne"))

    result = db.query(UserApproval).filter(
        UserApproval.user_id == user_id,
        UserApproval.version == current_version
    ).update({
        UserApproval.status: status,
        UserApproval.version: UserApproval.version + 1,
        UserApproval.rejection_reason: comment,
        UserApproval.process_time: melbourne_time
    })

    db.commit()
    return result == 1