from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

# Job table
class Job(SQLModel, table=True):
    __tablename__ = "job"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False, description="Job ID")
    user_id: int = Field(foreign_key="user.id", nullable=False, description="User ID")
    job_status: Optional[str] = Field(default=None, max_length=50, description="Job status")
    problem_name: Optional[str] = Field(default=None, max_length=255, description="Problem name")
    message: Optional[str] = Field(default=None, description="Message(e.g., success, failure)")
    performance_metric: Optional[str] = Field(default=None, max_length=100, description="Performance metric")
    problem_version: Optional[int] = Field(default=None, description="Problem version")
    userFriendlyProblemName: Optional[str] = Field(default=None, max_length=255, description="Display name")
    problem_description: Optional[str] = Field(default=None, description="Problem description")
    instance_space_type: Optional[str] = Field(default=None, max_length=50, description="Instance space type")
    projected_from: Optional[int] = Field(default=None, description="Source problem ID")
    projection_problem_type: Optional[str] = Field(default=None, max_length=50, description="Projection type")
    date_created: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    log_link: Optional[str] = Field(default=None,max_length=512,description="link of logs")
    completed_time: Optional[datetime] = Field(default=None,description="job completed time, even failed or completed")
    job_type: Optional[str] = Field(default=None, description="job type")
    csv_file_id: Optional[int] = Field(default=None, description="job's csv file ID")

    csv_file: Optional["CSVFile"] = Relationship(back_populates="job")