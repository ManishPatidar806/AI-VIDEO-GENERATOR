from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class TranscriptUploadResponse(BaseModel):
    message:str
    status:int
    success:bool


class APIResponse(BaseModel, Generic[T]):
    """Standardized API Response wrapper"""
    success: bool
    message: str
    data: Optional[T] = None
    status_code: int = 200


class ErrorResponse(BaseModel):
    """Standardized Error Response"""
    success: bool = False
    message: str
    error: Optional[str] = None
    status_code: int = 500