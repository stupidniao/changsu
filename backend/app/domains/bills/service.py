from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.bills.repository import BillRepository
from app.schemas.bills import BillCreate, BillRead, BillSummary


async def create_bill(db: AsyncSession, data: BillCreate, *, dry_run: bool = False) -> BillRead:
    if dry_run:
        return BillRead(**data.model_dump(), dry_run=True)

    bill = await BillRepository(db).create(data)
    await db.commit()
    return bill


async def list_recent_bills(
    db: AsyncSession,
    *,
    limit: int = 10,
    dry_run: bool = False,
) -> list[BillRead]:
    if dry_run:
        return []
    return await BillRepository(db).list_recent(limit=limit)


async def summarize_current_month(
    db: AsyncSession,
    *,
    now: datetime | None = None,
    dry_run: bool = False,
) -> BillSummary:
    current = now or datetime.now(timezone.utc)
    start_at = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start_at.month == 12:
        end_at = start_at.replace(year=start_at.year + 1, month=1)
    else:
        end_at = start_at.replace(month=start_at.month + 1)

    period = start_at.strftime("%Y-%m")
    if dry_run:
        return BillSummary(period=period)
    return await BillRepository(db).summarize(start_at=start_at, end_at=end_at, period=period)
