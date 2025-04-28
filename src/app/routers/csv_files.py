from fastapi import UploadFile, File, APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.database.session import get_session
from app.models.csv_files import CSVFile
from app.dependencies.auth import get_current_user_id
from io import StringIO

router = APIRouter(
    prefix="/csv",
    tags=["Csv"],
)

@router.post("/upload-csv")
async def upload_csv(
        job_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_session),
        user_id: int = Depends(get_current_user_id)
):
    content = await file.read()
    csv_file = CSVFile(
        filename=file.filename,
        file_content=content.decode("utf-8"),
        file_size=len(content),
        user_id=user_id,
        job_id=job_id
    )
    db.add(csv_file)
    db.commit()
    return {"message": "CSV file upload successfully", "file_id": csv_file.id}

@router.get("/download/{file_id}")
async def download_csv_file(
        file_id: int,
        db: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user_id)
):
    """
    download csv file
    """
    csv_file = db.query(CSVFile).filter(
        CSVFile.id == file_id,
        CSVFile.user_id == current_user_id  # makesure user only can download theirself files
    ).first()

    if not csv_file:
        raise HTTPException(
            status_code=404,
            detail="Can not found CSV file or no permitted"
        )
    file_stream = StringIO(csv_file.file_content)

    return StreamingResponse(
        file_stream,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={csv_file.filename}",
            "Content-Length": str(csv_file.file_size)
        }
    )