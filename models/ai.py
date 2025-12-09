from pydantic import BaseModel
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None  # Optional conversation context

class ChatResponse(BaseModel):
    reply: str