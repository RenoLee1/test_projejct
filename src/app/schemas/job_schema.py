from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel


class JobBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    job_status: Optional[str] = None
    problem_name: Optional[str] = None
    message: Optional[str] = None
    performance_metric: Optional[str] = None
    problem_version: Optional[int] = None
    userFriendlyProblemName: Optional[str] = None
    problem_description: Optional[str] = None
    instance_space_type: Optional[str] = None
    projected_from: Optional[int] = None
    projection_problem_type: Optional[str] = None
    log_link: Optional[str] = None
    completed_time: Optional[datetime] = None
    job_type: Optional[str] = None
    csv_file_id: Optional[int] = None


class JobResponse(JobBase):
    id: int
    user_id: int
    date_created: datetime
    

class JobList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    jobs: List[JobResponse]
    total: int


class CSVFileRead(SQLModel):
    id: int
    filename:str
    file_size:int
    upload_time: datetime
    job_id: Optional[int]
    user_id: Optional[int]
class JobReadWithCSV(SQLModel):
    id: int
    user_id: int
    job_status: Optional[str]
    problem_name: Optional[str]
    problem_description: Optional[str]

    csv_file:Optional[CSVFileRead] = None

