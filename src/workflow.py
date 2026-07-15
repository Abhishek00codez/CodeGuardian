from langgraph.graph import StateGraph, END

from src.state import AuditingState
from src.agents.auditor_node import auditor_node
from src.agents.fixer_node import fixer_node
from src.execution.local_tester import local_tester, route_after_test


def build_graph():
    graph = StateGraph(AuditingState)

    graph.add_node("auditor", auditor_node)
    graph.add_node("fixer", fixer_node)
    graph.add_node("tester", local_tester)

    graph.set_entry_point("auditor")
    graph.add_edge("auditor", "fixer")
    graph.add_edge("fixer", "tester")

    graph.add_conditional_edges(
        "tester",
        route_after_test,
        {
            "pass": END,
            "retry": "fixer",
        },
    )

    return graph.compile()


auditing_graph = build_graph()