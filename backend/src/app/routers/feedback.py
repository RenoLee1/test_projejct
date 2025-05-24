from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlmodel import Session
from typing import Optional, List

from app.database.session import get_session
from app.crud import feedback_crud
from app.schemas.feedback_schema import FeedbackList, FeedbackResponse, FeedbackCreate
from app.schemas.response import Response, success, error
from app.dependencies.auth import verify_admin_access

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@router.post("/", response_model=Response[FeedbackResponse])
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_session)
):
    """
    Create a new feedback entry
    """
    feedback = feedback_crud.create_feedback(
        db=db,
        username=feedback_data.username,
        email=feedback_data.email,
        category=feedback_data.category,
        message=feedback_data.message
    )
    
    return success(data=feedback)


@router.get("/", response_model=Response[FeedbackList])
async def get_feedback_list(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (e.g., 'unread', 'read', 'resolved')"),
    admin_id: int = Depends(verify_admin_access),
    db: Session = Depends(get_session)
):
    """
    Get a list of feedback with optional filtering and pagination.
    Admin access required.
    """
    feedbacks = feedback_crud.get_feedback_list(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        status=status
    )
    
    # Convert Feedback model objects to FeedbackResponse objects
    feedback_responses = [FeedbackResponse.model_validate(feedback) for feedback in feedbacks]
    
    total_count = feedback_crud.get_feedback_count(
        db=db,
        category=category,
        status=status
    )
    
    feedback_list = FeedbackList(
        feedbacks=feedback_responses,
        total=total_count
    )
    
    return success(data=feedback_list)


@router.get("/{feedback_id}", response_model=Response[FeedbackResponse])
async def get_feedback_by_id(
    feedback_id: int = Path(..., description="Feedback ID"),
    admin_id: int = Depends(verify_admin_access),
    db: Session = Depends(get_session)
):
    """
    Get a specific feedback by ID.
    Admin access required.
    """
    feedback = feedback_crud.get_feedback_by_id(db, feedback_id)
    if not feedback:
        return error(code=404, message="Feedback not found")
    return success(data=feedback)


@router.put("/{feedback_id}/status", response_model=Response[FeedbackResponse])
async def update_status(
    feedback_id: int = Path(..., description="Feedback ID"),
    status: str = Query(..., description="New status value (e.g., 'read', 'unread', 'resolved')"),
    admin_id: int = Depends(verify_admin_access),
    db: Session = Depends(get_session)
):
    """
    Update the status of a feedback.
    Admin access required.
    """
    feedback = feedback_crud.update_feedback_status(db, feedback_id, status)
    if not feedback:
        return error(code=404, message="Feedback not found")
    return success(data=feedback)


@router.delete("/{feedback_id}", response_model=Response)
async def delete_feedback(
    feedback_id: int = Path(..., description="Feedback ID"),
    admin_id: int = Depends(verify_admin_access),
    db: Session = Depends(get_session)
):
    """
    Delete a feedback by ID.
    Admin access required.
    """
    deleted = feedback_crud.delete_feedback(db, feedback_id)
    if not deleted:
        return error(code=404, message="Feedback not found")
    return success(message=f"Feedback with ID {feedback_id} has been deleted") 