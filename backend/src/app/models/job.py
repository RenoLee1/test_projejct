from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.problem import Problem
from app.models.job_metrics import JobMetrics
from app.models.user import User
from app.models.csv_files import CSVFile
from app.models.results import Results

class Job(SQLModel, table=True):
    __tablename__ = "job"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)  # Auto-increment job ID
    parent_job_id: Optional[int] = Field(default=None, foreign_key="job.id")  # Self-reference for hierarchical jobs
    user_id: int = Field(foreign_key="user.id", nullable=False)  # FK to User
    job_phase: Optional[str] = Field(default=None, description="Enum representing job phase")  # e.g., preprocessing, training
    job_status: Optional[str] = Field(default=None, description="Enum representing job status")  # e.g., running, completed
    job_name: Optional[str] = Field(default=None, max_length=255, description="Descriptive name for the job")

    metrics_id: Optional[int] = Field(default=None, foreign_key="job_metrics.id", unique=True)  # FK to performance metrics
    date_created: datetime = Field(default_factory=datetime.utcnow)  # Timestamp of job creation
    date_completed: Optional[datetime] = Field(default=None, description="Timestamp when job completed")  # Completion timestamp
    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")  # FK to problem metadata
    csv_file_id: Optional[int] = Field(default=None, foreign_key="csv_files.id")  # FK to input CSV file
    last_updated: Optional[datetime] = Field(default=None)  # Timestamp of last update

    # Relationships
    user: Optional["User"] = Relationship(back_populates="jobs")
    csv_file: Optional["CSVFile"] = Relationship(back_populates="job")
    problem: Optional["Problem"] = Relationship(back_populates="jobs")
    metrics: Optional["JobMetrics"] = Relationship(back_populates="job", sa_relationship_kwargs={"foreign_keys": "Job.metrics_id"})
    parent_job: Optional["Job"] = Relationship(sa_relationship_kwargs={"remote_side": "Job.id"})
    results: Optional["Results"] = Relationship(back_populates="job")  # One-to-one owned by Results





