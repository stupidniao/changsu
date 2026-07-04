from app.schemas.agent import AgentDebugTrace

_TRACE_STORE: dict[str, AgentDebugTrace] = {}


def save_trace(trace: AgentDebugTrace) -> None:
    _TRACE_STORE[trace.trace_id] = trace


def get_trace(trace_id: str) -> AgentDebugTrace | None:
    return _TRACE_STORE.get(trace_id)
