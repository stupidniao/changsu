from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.runner import run_agent_message
from app.deps import get_db
from app.schemas.agent import AgentMessageRequest, AgentMessageResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/messages")
async def create_agent_message(
    request: AgentMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> AgentMessageResponse:
    return await run_agent_message(request, db)
