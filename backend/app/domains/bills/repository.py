from datetime import datetime
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bills import Bill
from app.schemas.bills import BillCreate, BillRead, BillSummary


class BillRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: BillCreate) -> BillRead:
        bill = Bill(
            amount=Decimal(str(data.amount)),
            currency=data.currency,
            direction=data.direction,
            occurred_at=data.occurred_at,
            category=data.category,
            account=data.account,
            merchant=data.merchant,
            note=data.note,
            raw_text=data.raw_text,
            trace_id=data.trace_id,
        )
        self.db.add(bill)
        await self.db.flush()
        await self.db.refresh(bill)
        return self._to_read(bill)

    async def list_recent(self, limit: int = 10) -> list[BillRead]:
        stmt = select(Bill).order_by(Bill.occurred_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return [self._to_read(bill) for bill in result.scalars()]

    async def summarize(self, start_at: datetime, end_at: datetime, period: str) -> BillSummary:
        stmt: Select[tuple[str, Decimal | None, int]] = (
            select(Bill.direction, func.sum(Bill.amount), func.count(Bill.id))
            .where(Bill.occurred_at >= start_at, Bill.occurred_at < end_at)
            .group_by(Bill.direction)
        )
        result = await self.db.execute(stmt)

        summary = BillSummary(period=period)
        for direction, total, count in result.all():
            value = float(total or 0)
            if direction == "income":
                summary.total_income = value
            else:
                summary.total_expense = value
            summary.count += count
        return summary

    @staticmethod
    def _to_read(bill: Bill) -> BillRead:
        return BillRead(
            id=bill.id,
            amount=float(bill.amount),
            currency=bill.currency,
            direction=bill.direction,  # type: ignore[arg-type]
            occurred_at=bill.occurred_at,
            category=bill.category,
            account=bill.account,
            merchant=bill.merchant,
            note=bill.note,
            raw_text=bill.raw_text,
            trace_id=bill.trace_id,
        )
