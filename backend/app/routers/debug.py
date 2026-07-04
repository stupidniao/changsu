from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.runner import run_agent_message
from app.agents.tracing import get_trace
from app.deps import get_db
from app.domains.bills import create_bill, list_recent_bills, summarize_current_month
from app.schemas.agent import AgentDebugTrace, AgentMessageRequest, AgentMessageResponse
from app.schemas.bills import (
    BillCreate,
    DebugBillCreateResponse,
    DebugBillListResponse,
    DebugBillSummaryResponse,
)

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/agent-runs/{trace_id}")
async def get_agent_run(trace_id: str) -> AgentDebugTrace:
    trace = get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Agent run trace not found")
    return trace


@router.post("/agent-runs/replay")
async def replay_agent_run(
    request: AgentMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> AgentMessageResponse:
    replay_request = request.model_copy(
        update={
            "debug": request.debug.model_copy(update={"dry_run": True, "explain": True}),
        }
    )
    return await run_agent_message(replay_request, db)


@router.post("/bills/create")
async def debug_create_bill(
    request: BillCreate,
    dry_run: bool = True,
    db: AsyncSession = Depends(get_db),
) -> DebugBillCreateResponse:
    bill = await create_bill(db, request, dry_run=dry_run)
    return DebugBillCreateResponse(dry_run=dry_run, bill=bill)


@router.get("/bills/recent")
async def debug_list_recent_bills(
    limit: int = 10,
    dry_run: bool = True,
    db: AsyncSession = Depends(get_db),
) -> DebugBillListResponse:
    bills = await list_recent_bills(db, limit=limit, dry_run=dry_run)
    return DebugBillListResponse(dry_run=dry_run, bills=bills)


@router.get("/bills/summary")
async def debug_summarize_bills(
    dry_run: bool = True,
    db: AsyncSession = Depends(get_db),
) -> DebugBillSummaryResponse:
    summary = await summarize_current_month(db, dry_run=dry_run)
    return DebugBillSummaryResponse(dry_run=dry_run, summary=summary)
