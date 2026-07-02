from app.agents.graph import agent_graph, build_agent_graph


def test_agent_graph_compiles() -> None:
    graph = build_agent_graph()
    assert graph is not None
    assert agent_graph is not None
