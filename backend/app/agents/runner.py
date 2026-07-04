from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tools import (
    BillsToolContext,
    call_bills_tool,
    candidate_tools_for_intent,
    classify_bills_intent,
    extract_bill_create_args,
)
from app.agents.tracing import save_trace
from app.schemas.agent import (
    AgentDebugTrace,
    AgentMessageRequest,
    AgentMessageResponse,
    ToolCallTrace,
    TraceStep,
)


async def run_agent_message(request: AgentMessageRequest, db: AsyncSession) -> AgentMessageResponse:
    trace_id = str(uuid4())
    intent = classify_bills_intent(request.message)
    candidate_tools = candidate_tools_for_intent(intent)
    trace = AgentDebugTrace(
        trace_id=trace_id,
        conversation_id=request.conversation_id,
        intent=intent,
        candidate_tools=candidate_tools,
        dry_run=request.debug.dry_run,
        explain=request.debug.explain,
    )
    trace.steps.append(
        TraceStep(
            kind="intent",
            message="Classified the user message.",
            data={"message": request.message, "intent": intent},
        )
    )

    reply = "我还没判断出要怎么处理这句话。你可以先试试：今天午饭 38 元。"
    if intent == "create_bill":
        reply = await _handle_create_bill(request, db, trace)
    elif intent == "list_recent_bills":
        reply = await _handle_list_recent(request, db, trace)
    elif intent == "summarize_bills":
        reply = await _handle_summary(request, db, trace)

    trace.steps.append(TraceStep(kind="reply", message="Generated final reply.", data={"reply": reply}))
    save_trace(trace)

    include_trace = request.debug.dry_run or request.debug.explain
    return AgentMessageResponse(
        trace_id=trace_id,
        reply=reply,
        debug_trace=trace if include_trace else None,
    )


async def _handle_create_bill(
    request: AgentMessageRequest,
    db: AsyncSession,
    trace: AgentDebugTrace,
) -> str:
    args = extract_bill_create_args(request.message, trace.trace_id)
    trace.steps.append(
        TraceStep(kind="tool_args", message="Extracted create_bill arguments.", data=args)
    )
    tool_call = ToolCallTrace(name="create_bill", args=_json_safe(args))
    trace.tool_calls.append(tool_call)

    result = await call_bills_tool(
        "create_bill",
        args,
        BillsToolContext(db=db, trace_id=trace.trace_id, dry_run=request.debug.dry_run),
    )
    tool_call.result = result

    if not result.get("ok"):
        return "我需要知道金额才能记账。"

    bill = result["bill"]
    prefix = "调试预览：" if request.debug.dry_run else "已记账："
    return f"{prefix}{bill['category']} {bill['amount']} {bill['currency']}。"


async def _handle_list_recent(
    request: AgentMessageRequest,
    db: AsyncSession,
    trace: AgentDebugTrace,
) -> str:
    args = {"limit": 10}
    tool_call = ToolCallTrace(name="list_recent_bills", args=args)
    trace.tool_calls.append(tool_call)
    result = await call_bills_tool(
        "list_recent_bills",
        args,
        BillsToolContext(db=db, trace_id=trace.trace_id, dry_run=request.debug.dry_run),
    )
    tool_call.result = result
    if request.debug.dry_run:
        return "调试预览：会查询最近 10 条账单。"

    bills = result.get("bills", [])
    if not bills:
        return "最近还没有账单。"
    return f"最近有 {len(bills)} 条账单。"


async def _handle_summary(
    request: AgentMessageRequest,
    db: AsyncSession,
    trace: AgentDebugTrace,
) -> str:
    args: dict[str, str] = {}
    tool_call = ToolCallTrace(name="summarize_current_month", args=args)
    trace.tool_calls.append(tool_call)
    result = await call_bills_tool(
        "summarize_current_month",
        args,
        BillsToolContext(db=db, trace_id=trace.trace_id, dry_run=request.debug.dry_run),
    )
    tool_call.result = result
    summary = result["summary"]
    if request.debug.dry_run:
        return f"调试预览：会汇总 {summary['period']} 的账单。"
    return (
        f"{summary['period']} 支出 {summary['total_expense']} CNY，"
        f"收入 {summary['total_income']} CNY。"
    )


def _json_safe(args: dict) -> dict:
    return {
        key: value.isoformat() if hasattr(value, "isoformat") else value
        for key, value in args.items()
    }
