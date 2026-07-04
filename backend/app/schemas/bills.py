from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

BillDirection = Literal["expense", "income"]


class BillCreate(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "CNY"
    direction: BillDirection = "expense"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: str = "uncategorized"
    account: str = "default"
    merchant: str | None = None
    note: str | None = None
    raw_text: str | None = None
    trace_id: str | None = None


class BillRead(BaseModel):
    id: int | None = None
    amount: float
    currency: str
    direction: BillDirection
    occurred_at: datetime
    category: str
    account: str
    merchant: str | None = None
    note: str | None = None
    raw_text: str | None = None
    trace_id: str | None = None
    dry_run: bool = False


class BillSummary(BaseModel):
    period: str
    total_expense: float = 0
    total_income: float = 0
    count: int = 0


class DebugBillCreateResponse(BaseModel):
    dry_run: bool
    bill: BillRead


class DebugBillListResponse(BaseModel):
    dry_run: bool
    bills: list[BillRead]


class DebugBillSummaryResponse(BaseModel):
    dry_run: bool
    summary: BillSummary
