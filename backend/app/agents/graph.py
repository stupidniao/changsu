from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.tools import classify_bills_intent


class AgentState(TypedDict):
    """Shared state for the Changsu agent graph."""

    messages: list[str]
    intent: str | None


def _classify_intent(state: AgentState) -> AgentState:
    latest_message = state["messages"][-1] if state["messages"] else ""
    return {**state, "intent": classify_bills_intent(latest_message)}


def build_agent_graph():
    """Build the first bills-oriented agent skeleton."""
    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", _classify_intent)
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", END)
    return graph.compile()


agent_graph = build_agent_graph()
