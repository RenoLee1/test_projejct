from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import httpx
from typing import Optional
from pathlib import Path

router = APIRouter(
    prefix="/log",
    tags=["Log"],
)

# test URL
MATILDA_LOG_URL = "https://matilda.unimelb.edu.au/matilda/usersdata/Krystal/travelling_salesman_problem/matilda_logs.txt"


@router.get("/")
async def download_matilda_log(
        file_url: str = Query(..., description="The URL of the file to download")
):
    """
    Download the file in txt from a link
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            response.raise_for_status()

            # get filename from url
            filename = Path(MATILDA_LOG_URL).name

            return StreamingResponse(
                response.iter_bytes(),
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Matilda server return failed: {e.response.status_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"download failed: {str(e)}"
        )


@router.get("/get-matilda-log")
async def get_matilda_log(
        file_url: str = Query(..., description="The URL of the file to download")
):
    """
    Get content of link in JSON format
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            response.raise_for_status()

            filename = Path(MATILDA_LOG_URL).name
            content = response.text

            return {
                "filename": filename,
                "content": content,
                "size": len(content.encode('utf-8')),
                "download_url": MATILDA_LOG_URL
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Acquired log content failed: {str(e)}"
        )