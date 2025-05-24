from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Results(SQLModel, table=True):
    __tablename__ = "results"

    id: Optional[int] = Field(default=None, primary_key=True)
    field_1: str = Field(description="Primary result output")
    field_2: str = Field(description="Secondary result output")
    job_id: int = Field(foreign_key="job.id", nullable=False)

    # Relationships
    job: Optional["Job"] = Relationship(back_populates="results")
