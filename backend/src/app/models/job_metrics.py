from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class JobMetrics(SQLModel, table=True):
    __tablename__ = "job_metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    metric_1: float = Field(description="Primary job metric")
    optional_metric_2: Optional[float] = Field(default=None, description="Secondary optional metric")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Start time of metric collection")
    last_updated: Optional[datetime] = Field(default=None, description="Timestamp of last update")

    # Relationships
    job: Optional["Job"] = Relationship(back_populates="metrics", sa_relationship_kwargs={"foreign_keys": "Job.metrics_id", "uselist": False})