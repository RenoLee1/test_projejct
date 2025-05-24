from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status, Form, UploadFile, File
from sqlmodel import Session
from datetime import datetime
import csv
from io import StringIO
from app.database.session import get_session
from app.crud import job_crud, csv_files_crud, problem_crud
from app.schemas.job_schema import JobResponse, JobList, JobReadWithCSV
from app.schemas.response import Response, success, error
from app.dependencies.auth import get_current_user_id
from app.models.problem import Problem  # 必须 import 以获得类型信息

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.get("/", response_model=Response[JobList])
async def list_jobs(
    db: Session = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Get all jobs for the current user"""
    jobs = job_crud.get_jobs_by_user(db, user_id)
    # Convert SQLModel objects to JobResponse objects
    jobs_list = [JobResponse.model_validate(job) for job in jobs]
    total = len(jobs)
    return success(data=JobList(jobs=jobs_list, total=total))


@router.get("/{id}", response_model=Response[JobResponse])
async def get_job_detail(
    id: int = Path(..., description="Job ID"),
    db: Session = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Get job details by ID"""
    job = job_crud.get_job(db, id)
    
    if not job:
        return error(code=404, message="Job not found")
        
    if job.user_id != user_id:
        return error(code=403, message="Not authorized to access this job")
        
    return success(data=JobResponse.model_validate(job))


@router.delete("/{id}", response_model=Response)
async def delete_job(
    id: int = Path(..., description="Job ID"),
    db: Session = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a job by ID"""
    db_job = job_crud.get_job(db, id)
    
    if not db_job:
        return error(code=404, message="Job not found")
    
    if db_job.user_id != user_id:
        return error(code=403, message="Not authorized to delete this job")
    
    success_delete = job_crud.delete_job(db, id)
    if success_delete:
        return success(message="Job deleted successfully")
    else:
        return error(message="Failed to delete job")



@router.post("/create_new_job", response_model=JobReadWithCSV)
async def create_job_with_csv(
        problem: Problem = Depends(problem_crud.validate_problem_id),
        job_phase: Optional[str] = Form("preprocessing"),
        job_name: Optional[str] = Form(None),
        current_user_id: int = Depends(get_current_user_id),
        csv_file: UploadFile = File(...),
        db: Session = Depends(get_session)
):
    """
    Create a new job with CSV file
    """

    if not csv_file.filename.lower().endswith('.csv'):
        raise HTTPException(400, "only .csv files are allowed")

    try:
        content = await csv_file.read()
        content_str = content.decode('utf-8')
        list(csv.reader(StringIO(content_str)))
    except Exception as e:
        raise HTTPException(400, f"CSV file are invalid: {str(e)}")

    try:

        job_data = {
            "problem_id": problem.id,
            "job_phase": job_phase,
            "job_name": job_name
        }
        job = job_crud.create_job_with_csv(db,job_data=job_data,user_id=current_user_id,csv_content=content_str)

        return job

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"create failed: {str(e)}")