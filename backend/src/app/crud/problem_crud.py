from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from app.models.problem import Problem
from app.database.session import get_session

def validate_problem_id(
    problem_id: int,
    db: Session = Depends(get_session)
) -> Problem:
    """check problem_id exist，and return Problem object"""
    problem = db.exec(select(Problem).where(Problem.id == problem_id)).first()
    if not problem:
        raise HTTPException(status_code=400, detail=f"Invalid problem_id: {problem_id} not found")
    return problem
