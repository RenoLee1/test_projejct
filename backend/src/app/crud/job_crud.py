from typing import List, Optional
import uuid
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.models.job import Job
from app.models.results import Results
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
        try:
            # First delete all associated results
            results_list = db.exec(select(Results).where(Results.job_id == id)).all()
            for result in results_list:
                db.delete(result)
            db.flush()
            
            # Save csv_file_id for later check
            csv_file_id = db_job.csv_file_id
            
            # Delete the job record
            db.delete(db_job)
            db.commit()
            
            # If csv_file_id exists, check if any other jobs reference this file
            if csv_file_id:
                # Check if any other jobs reference this CSV file
                other_jobs = db.exec(select(Job).where(Job.csv_file_id == csv_file_id)).first()
                if not other_jobs:
                    # If no other jobs reference this CSV file, delete it
                    delete_csv(db, csv_file_id)
            
            return True
        except Exception as e:
            db.rollback()
            print(f"Error deleting job: {e}")
            return False
    return False

def create_job_with_csv(db: Session, job_data: dict, user_id: int,csv_content: str) -> Job:
    """
    Create a new job and store csv_file
    """
    # db.begin()
    try:
        job = Job(
            **job_data,
            user_id=user_id,
            job_status="pending",
            date_created=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        db.add(job)
        db.flush()

        csv_file = create_csv(db, str(uuid.uuid4())+".csv", csv_content)

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
    statement = select(Job).where(
        Job.id == job_id,
        Job.user_id == user_id
    )
    result = db.exec(statement).first()
    return result

