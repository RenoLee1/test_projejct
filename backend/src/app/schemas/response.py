from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

# Generic API response
class Response(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True

def success(*, data: Any = None, message: str = "success") -> Response:
    """
    Success response
    """
    return Response(
        code=200,
        message=message,
        data=data
    )

def error(*, code: int = 400, message: str = "error") -> Response:
    """
    Error response
    """
    return Response(
        code=code,
        message=message
    ) 