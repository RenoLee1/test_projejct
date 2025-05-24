from fastapi import UploadFile, File, APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.crud.csv_files_crud import calculate_checksum
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
        db: Session = Depends(get_session)
):
    content = await file.read()
    file_content = content.decode("utf-8")    
    csv_file = CSVFile(
        filename=file.filename,
        file_content=file_content,
        file_size=len(content),
        job_id=job_id,
        checksum=calculate_checksum(file_content)
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