from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    """Shared state for the Changsu agent graph."""

    messages: list[str]


def _noop(_state: AgentState) -> AgentState:
    return _state


def build_agent_graph():
    """Build a minimal LangGraph skeleton (start -> end, no business logic yet)."""
    graph = StateGraph(AgentState)
    graph.add_node("noop", _noop)
    graph.add_edge(START, "noop")
    graph.add_edge("noop", END)
    return graph.compile()


agent_graph = build_agent_graph()
