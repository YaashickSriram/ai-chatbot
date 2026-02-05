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
        # 1️⃣ Run tool selection + execution safely
        tool_response = await run_in_threadpool(agent.run, query)

        # 2️⃣ Defensive validation FIRST
        if not isinstance(tool_response, dict):
            logger.error("Agent returned non-dict response")
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from agent"
            )

        # 3️⃣ Generate natural language answer
        answer = agent.generate_answer(query, tool_response)

        logger.info(
            f"Chat processed successfully | tool={tool_response.get('tool')}"
        )

        return {
            "tool": tool_response.get("tool"),
            "answer": answer,
            "results": tool_response.get("results"),
            "value": tool_response.get("value"),
        }

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception:
        logger.exception("Unhandled exception during chat execution")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing query"
        )
