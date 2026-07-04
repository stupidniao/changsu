from httpx import ASGITransport, AsyncClient
import pytest

from app.main import app

pytestmark = pytest.mark.asyncio


async def test_debug_create_bill_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/debug/bills/create?dry_run=true",
            json={
                "amount": 38,
                "currency": "CNY",
                "direction": "expense",
                "category": "food",
                "account": "debug",
                "note": "今天午饭 38 元",
                "raw_text": "今天午饭 38 元",
                "trace_id": "test-trace",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["bill"]["amount"] == 38
    assert body["bill"]["category"] == "food"
    assert body["bill"]["dry_run"] is True


async def test_debug_recent_bills_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/debug/bills/recent?limit=10&dry_run=true")

    assert response.status_code == 200
    assert response.json() == {"dry_run": True, "bills": []}


async def test_debug_summary_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/debug/bills/summary?dry_run=true")

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["summary"]["total_expense"] == 0
    assert body["summary"]["total_income"] == 0
