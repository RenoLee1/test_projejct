import hashlib
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import select
from sqlalchemy.orm import Session
from app.models.csv_files import CSVFile

def calculate_checksum(content: str) -> str:
    """Generate SHA256 checksum for file content"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def create_csv(db: Session, filename: str, content: str) -> CSVFile:
    """Create a new CSV file"""
    csv_file = CSVFile(
        filename=filename,
        file_content=content,
        file_size=len(content.encode("utf-8")),
        upload_time=datetime.now(timezone.utc),
        checksum=calculate_checksum(content)
    )
    db.add(csv_file)
    db.flush()  # create but not commit
    return csv_file


def get_csv(db: Session, id: int) -> Optional[CSVFile]:
    """Get a CSV file by its ID"""
    return db.exec(select(CSVFile).where(CSVFile.id == id)).first()


def delete_csv(db: Session, id: int) -> bool:
    """Delete CSV file by ID"""
    db_csv = get_csv(db, id)
    if db_csv:
        db.delete(db_csv)
        db.commit()
        return True
    return False
