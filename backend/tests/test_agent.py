from app.agents.graph import agent_graph, build_agent_graph
from app.agents.tools import classify_bills_intent, extract_bill_create_args


def test_agent_graph_compiles() -> None:
    graph = build_agent_graph()
    assert graph is not None
    assert agent_graph is not None


def test_agent_graph_classifies_bill_creation() -> None:
    graph = build_agent_graph()
    result = graph.invoke({"messages": ["今天午饭 38 元"], "intent": None})
    assert result["intent"] == "create_bill"


def test_bills_tool_extracts_structured_args() -> None:
    args = extract_bill_create_args("今天午饭 38 元", trace_id="trace-1")
    assert args["amount"] == 38
    assert args["category"] == "food"
    assert args["direction"] == "expense"
    assert args["trace_id"] == "trace-1"


def test_bills_intent_classification() -> None:
    assert classify_bills_intent("最近账单") == "list_recent_bills"
    assert classify_bills_intent("本月花了多少") == "summarize_bills"
    assert classify_bills_intent("今天咖啡 20 元") == "create_bill"
