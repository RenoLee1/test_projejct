from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Text, Relationship

class CSVFile(SQLModel, table=True):
    __tablename__ = "csv_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    file_content: str = Field(sa_type=Text())  # store file content
    file_size: int
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    job_id: Optional[int] = Field(default=None,foreign_key="job.id",unique=True)
    user_id: int = Field(foreign_key="user.id")

    job: Optional["Job"] = Relationship(back_populates="csv_file")
