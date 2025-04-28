from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
from app.models.csv_files import CSVFile

def create_csv(db: Session, filename: str, content: str, user_id: int, job_id) -> CSVFile:
    """Create a new CSV file"""
    csv_file = CSVFile(
        filename=filename,
        file_content=content,
        file_size=len(content.encode('utf-8')),
        upload_time=datetime.utcnow(),
        user_id=user_id,
        job_id=job_id
    )
    db.add(csv_file)
    db.flush() # create but not commit
    return csv_file

def get_csv(db: Session, id:int) -> Optional[CSVFile]:
    """Get a CSV file by csv_id and user_id"""
    return db.exec(select(CSVFile).where(CSVFile.id == id)).first()

def delete_csv(db: Session, id: int) -> bool:
    """Delete job by ID"""
    db_csv = get_csv(db, id)
    if db_csv:
        db.delete(db_csv)
        db.commit()
        return True
    return False