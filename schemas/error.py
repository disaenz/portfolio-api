from pydantic import BaseModel

class APIError(BaseModel):
    success: bool = False
    error:   str

class APIError(BaseModel):
    error: str