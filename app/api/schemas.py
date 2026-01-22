from pydantic import BaseModel
from typing import Any, Dict, List, Optional


# -----------------------------
# Chat Request Schema
# -----------------------------
class ChatRequest(BaseModel):
    query: str


# -----------------------------
# Chat Response Schema
# -----------------------------
class ChatResponse(BaseModel):
    tool: Optional[Any]
    results: Optional[List[Dict[str, Any]]] = None
    value: Optional[Any] = None

# -----------------------------
# Error Response Schema
# -----------------------------

class ErrorResponse(BaseModel):
    error_code: str
    message: str

