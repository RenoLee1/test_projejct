from pydantic import BaseModel
from typing import Optional

class LogContent(BaseModel):
    content: str
    filename: str
    size: int  # file size

class LogDownloadResponse(BaseModel):
    log: LogContent