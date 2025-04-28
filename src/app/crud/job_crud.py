from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from app.models.job import Job
from app.crud.csv_files_crud import create_csv, delete_csv


def get_job(db: Session, id: int) -> Optional[Job]:
    """Get job by ID"""
    return db.exec(select(Job).where(Job.id == id)).first()


def get_jobs_by_user(db: Session, user_id: int) -> List[Job]:
    """Get all jobs for a specific user"""
    return db.exec(select(Job).where(Job.user_id == user_id)).all()


def delete_job(db: Session, id: int) -> bool:
    """Delete job by ID"""
    db_job = get_job(db, id)
    if db_job:
        delete_csv(db,db_job.csv_file_id)
        db.delete(db_job)
        db.commit()
        return True
    return False

def create_job_with_csv(db: Session,job_data: dict,user_id: int,csv_content: str) -> Job:
    """
    Create a new job and store csv_file
    """
    db.begin()
    try:
        job = Job(
            **job_data,
            user_id=user_id,
            job_status="pending",
            date_created=datetime.utcnow()
        )
        db.add(job)
        db.flush()

        csv_file = create_csv(db,job_data["problem_name"],csv_content, user_id, job.id)

        if not csv_file:
            db.rollback()
            raise ValueError("CSV Invalid")

        job.csv_file_id = csv_file.id

        db.commit()
        db.refresh(job)
        return job

    except Exception as e:
        db.rollback()
        raise

def get_job_with_csv(db: Session, job_id: int, user_id: int) -> Optional[Job]:
    return db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == user_id
    ).first()


