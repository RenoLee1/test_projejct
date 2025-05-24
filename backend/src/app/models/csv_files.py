from typing import Optional
from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field, Text

class CSVFile(SQLModel, table=True):
    __tablename__ = "csv_files"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)  # Auto-incremented file ID
    filename: str = Field(max_length=255, description="Filename (UUID or hashed)")  # Short name, e.g., UUID
    file_content: str = Field(nullable=False, description="Raw CSV contents")  # Full file content
    file_size: int = Field(description="File size in bytes")  # Byte count
    upload_time: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")  # When uploaded
    checksum: str = Field(max_length=255, description="SHA256 or similar checksum")  # Content hash

    job: Optional["Job"] = Relationship(back_populates="csv_file")
