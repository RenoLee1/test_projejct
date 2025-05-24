from typing import List, Optional
from sqlmodel import Session, select
from app.models.feedback import Feedback


def get_feedback_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None
) -> List[Feedback]:
    """
    Get list of feedback with optional filtering by category and status
    Returns a list of Feedback model objects
    """
    # Create base query
    query = select(Feedback)
    
    if category:
        query = query.where(Feedback.category == category)
    
    if status is not None:  # can be "unread" or "read"
        query = query.where(Feedback.status == status)
    
    # Sort by most recent first
    query = query.order_by(Feedback.created_time.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query and get results
    feedbacks = db.exec(query).all()
    
    return feedbacks


def get_feedback_by_id(db: Session, feedback_id: int) -> Optional[Feedback]:
    """
    Get a specific feedback by ID
    """
    query = select(Feedback).where(Feedback.id == feedback_id)
    return db.exec(query).first()


def get_feedback_count(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = None
) -> int:
    """
    Get total count of feedback with optional filtering
    """
    query = select(Feedback)
    
    if category:
        query = query.where(Feedback.category == category)
    
    if status is not None:
        query = query.where(Feedback.status == status)
    
    return len(db.exec(query).all())


def update_feedback_status(db: Session, feedback_id: int, status: str) -> Optional[Feedback]:
    """
    Update the status of a feedback
    """
    feedback = get_feedback_by_id(db, feedback_id)
    if feedback:
        feedback.status = status
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
    return feedback


def create_feedback(
    db: Session,
    username: str,
    email: str,
    category: str,
    message: str,
    status: str = "unread"
) -> Feedback:
    """
    Create a new feedback
    """
    feedback = Feedback(
        username=username,
        email=email,
        category=category,
        message=message,
        status=status
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback


def delete_feedback(db: Session, feedback_id: int) -> bool:
    """
    Delete a feedback by ID
    
    Returns:
        bool: True if feedback was deleted, False if feedback wasn't found
    """
    feedback = get_feedback_by_id(db, feedback_id)
    if not feedback:
        return False
    
    db.delete(feedback)
    db.commit()
    return True 