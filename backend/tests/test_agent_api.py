from httpx import ASGITransport, AsyncClient
import pytest

from app.main import app

pytestmark = pytest.mark.asyncio


async def test_agent_message_returns_debug_trace_in_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agent/messages",
            json={
                "message": "今天午饭 38 元",
                "debug": {"dry_run": True, "explain": True},
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "调试预览：food 38.0 CNY。"
    assert body["debug_trace"]["intent"] == "create_bill"
    assert body["debug_trace"]["tool_calls"][0]["name"] == "create_bill"
    assert body["debug_trace"]["tool_calls"][0]["result"]["bill"]["dry_run"] is True


async def test_agent_trace_can_be_fetched_by_trace_id() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post(
            "/agent/messages",
            json={
                "message": "本月花了多少",
                "debug": {"dry_run": True, "explain": True},
            },
        )
        trace_id = create_response.json()["trace_id"]
        trace_response = await client.get(f"/debug/agent-runs/{trace_id}")

    assert trace_response.status_code == 200
    assert trace_response.json()["trace_id"] == trace_id
    assert trace_response.json()["intent"] == "summarize_bills"


async def test_agent_replay_forces_debug_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/debug/agent-runs/replay",
            json={"message": "最近账单", "debug": {"dry_run": False, "explain": False}},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["debug_trace"]["dry_run"] is True
    assert body["debug_trace"]["explain"] is True
    assert body["reply"] == "调试预览：会查询最近 10 条账单。"


async def test_debug_create_bill_api_returns_dry_run_bill() -> None:
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
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["bill"]["amount"] == 38
    assert body["bill"]["category"] == "food"
    assert body["bill"]["dry_run"] is True


async def test_debug_recent_bills_api_supports_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/debug/bills/recent?limit=5&dry_run=true")

    assert response.status_code == 200
    assert response.json() == {"dry_run": True, "bills": []}


async def test_debug_summary_api_supports_dry_run() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/debug/bills/summary?dry_run=true")

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["summary"]["total_expense"] == 0
    assert body["summary"]["total_income"] == 0
