from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.bills import create_bill, list_recent_bills, summarize_current_month
from app.schemas.bills import BillCreate

BillIntent = Literal["create_bill", "list_recent_bills", "summarize_bills", "unknown"]


@dataclass(frozen=True)
class BillsToolContext:
    db: AsyncSession
    trace_id: str
    dry_run: bool = False


def classify_bills_intent(message: str) -> BillIntent:
    if any(keyword in message for keyword in ["汇总", "统计", "本月", "这个月", "花了多少"]):
        return "summarize_bills"
    if any(keyword in message for keyword in ["最近", "查询", "列表", "明细"]):
        return "list_recent_bills"
    if re.search(r"\d+(?:\.\d+)?\s*元?", message):
        return "create_bill"
    return "unknown"


def candidate_tools_for_intent(intent: BillIntent) -> list[str]:
    if intent == "create_bill":
        return ["create_bill"]
    if intent == "list_recent_bills":
        return ["list_recent_bills"]
    if intent == "summarize_bills":
        return ["summarize_current_month"]
    return []


def extract_bill_create_args(message: str, trace_id: str) -> dict[str, Any]:
    amount_match = re.search(r"(\d+(?:\.\d+)?)\s*元?", message)
    if amount_match is None:
        return {"missing_fields": ["amount"], "raw_text": message, "trace_id": trace_id}

    category = _infer_category(message)
    merchant = _infer_merchant(message)
    return {
        "amount": float(amount_match.group(1)),
        "currency": "CNY",
        "direction": "income" if any(word in message for word in ["收入", "工资", "到账"]) else "expense",
        "occurred_at": datetime.now(timezone.utc),
        "category": category,
        "account": "default",
        "merchant": merchant,
        "note": message,
        "raw_text": message,
        "trace_id": trace_id,
    }


async def call_bills_tool(
    name: str,
    args: dict[str, Any],
    context: BillsToolContext,
) -> dict[str, Any]:
    if name == "create_bill":
        if args.get("missing_fields"):
            return {"ok": False, "missing_fields": args["missing_fields"]}
        bill = await create_bill(context.db, BillCreate(**args), dry_run=context.dry_run)
        return {"ok": True, "bill": bill.model_dump(mode="json")}

    if name == "list_recent_bills":
        bills = await list_recent_bills(context.db, limit=int(args.get("limit", 10)), dry_run=context.dry_run)
        return {"ok": True, "bills": [bill.model_dump(mode="json") for bill in bills]}

    if name == "summarize_current_month":
        summary = await summarize_current_month(context.db, dry_run=context.dry_run)
        return {"ok": True, "summary": summary.model_dump(mode="json")}

    return {"ok": False, "error": f"Unknown bills tool: {name}"}


def _infer_category(message: str) -> str:
    rules = [
        ("food", ["饭", "午饭", "晚饭", "早餐", "咖啡", "奶茶", "餐", "吃"]),
        ("transport", ["打车", "地铁", "公交", "高铁", "机票", "停车"]),
        ("shopping", ["买", "购物", "淘宝", "京东"]),
        ("housing", ["房租", "水电", "物业"]),
        ("health", ["医院", "药", "体检"]),
    ]
    for category, keywords in rules:
        if any(keyword in message for keyword in keywords):
            return category
    return "uncategorized"


def _infer_merchant(message: str) -> str | None:
    for marker in ["在", "@"]:
        if marker in message:
            candidate = message.split(marker, maxsplit=1)[1].strip()
            if candidate:
                return candidate[:64]
    return None
