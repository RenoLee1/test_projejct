from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel


# Shared job base for responses
class JobBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_status: Optional[str] = None
    problem_id: Optional[int] = None
    message: Optional[str] = None
    performance_metric: Optional[str] = None
    problem_version: Optional[int] = None
    projected_from: Optional[int] = None
    projection_problem_type: Optional[str] = None
    completed_time: Optional[datetime] = None
    job_type: Optional[str] = None
    csv_file_id: Optional[int] = None
    job_phase: Optional[str] = None
    job_name: Optional[str] = None
    metrics_id: Optional[int] = None
    parent_job_id: Optional[int] = None
    last_updated: Optional[datetime] = None
    date_completed: Optional[datetime] = None


# Response for single job entity
class JobResponse(JobBase):
    id: int
    user_id: int
    date_created: datetime


# For paginated lists of jobs
class JobList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobs: List[JobResponse]
    total: int


# CSV file read response (cleaned up)
class CSVFileRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_size: int
    upload_time: datetime
    checksum: str


# Job response with nested CSV file
class JobReadWithCSV(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_status: Optional[str]
    problem_id: Optional[int]
    date_created: datetime
    date_completed: Optional[datetime] = None
    csv_file: Optional[CSVFileRead] = None
