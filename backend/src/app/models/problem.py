from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Problem(SQLModel, table=True):
    __tablename__ = "problem"

    id: Optional[int] = Field(default=None, primary_key=True)
    problem_type: str = Field(description="Problem type (e.g., classification, regression)")
    features: str = Field(max_length=255, description="Encoded features string")
    algorithms: str = Field(max_length=255, description="Algorithms applicable to this problem")
    csv_file_id: Optional[int] = Field(default=None, foreign_key="csv_files.id")

    # Relationships
    jobs: List["Job"] = Relationship(back_populates="problem")
