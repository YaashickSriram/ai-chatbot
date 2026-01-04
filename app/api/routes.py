from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from  typing import Optional

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    metadata: dict

@router.post("/chat/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Main endpoint for user queries
    """
    # Invoke ReAct agent
    # Return formatted response
    pass

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}