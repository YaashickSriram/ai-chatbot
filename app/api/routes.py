from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
import logging

from app.api.schemas import ChatRequest, ChatResponse
from app.api.dependencies import get_agent
from app.agents.reAct_agents import ReActAgent

logger = logging.getLogger("chat_api")

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent: ReActAgent = Depends(get_agent)
):
    query = (request.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    logger.info(f"Incoming chat query: {query}")

    try:
        # run agent.run in a worker thread so event loop isn't blocked
        response = await run_in_threadpool(agent.run, query)

        if not isinstance(response, dict):
            logger.error("Agent returned non-dict response")
            raise HTTPException(status_code=500, detail="Invalid response format from agent")

        logger.info(f"Chat processed successfully | tool={response.get('tool')}")
        return response

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception:
        logger.exception("Unhandled exception during chat execution")
        raise HTTPException(status_code=500, detail="Internal server error while processing query")
