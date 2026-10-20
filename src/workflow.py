from typing import TypedDict
from langgraph.graph import StateGraph, END

from .parser import parse_code
from .agents import critic_agent, coder_agent
from .validator import run_tests

class WorkflowState(TypedDict):
    source_code: str
    test_code: str
    ast_context: dict
    review_feedback: str
    test_output: str
    retry_count: int
    max_retries: int
    final_status: str

def ast_node(state: WorkflowState) -> WorkflowState:
    res = parse_code(state["source_code"])
    if res["status"] == "error":
        err = res["syntax_error"]
        state["review_feedback"] = f"Syntax Error: {err['msg']} at line {err['lineno']}\nCode: {err['text']}"
        state["ast_context"] = {}
    else:
        state["ast_context"] = res["ast_context"]
    return state

def critic_node(state: WorkflowState) -> WorkflowState:
    if state.get("review_feedback"): # Skip if syntax error already caught
        return state

    feedback = critic_agent(state["source_code"], state["ast_context"])
    state["review_feedback"] = feedback
    return state

def coder_node(state: WorkflowState) -> WorkflowState:
    new_code = coder_agent(state["source_code"], state["review_feedback"], state.get("test_output", ""))
    state["source_code"] = new_code
    # Clear test output for the next validation run
    state["test_output"] = ""
    return state

def validator_node(state: WorkflowState) -> WorkflowState:
    res = run_tests(state["source_code"], state.get("test_code", ""))
    if res["success"]:
        state["final_status"] = "success"
    else:
        state["final_status"] = "failed"
        err = res.get("error", "")
        out = res.get("output", "")
        state["test_output"] = f"Output:\n{out}\nError:\n{err}"
        state["retry_count"] = state.get("retry_count", 0) + 1
    return state

def router(state: WorkflowState) -> str:
    if state.get("final_status") == "success":
        return "end"
    if state.get("retry_count", 0) >= state.get("max_retries", 3):
        return "end"
    return "coder"

def create_workflow():
    workflow = StateGraph(WorkflowState)

    workflow.add_node("ast", ast_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("validator", validator_node)

    workflow.set_entry_point("ast")

    workflow.add_edge("ast", "critic")
    workflow.add_edge("critic", "coder")
    workflow.add_edge("coder", "validator")

    workflow.add_conditional_edges(
        "validator",
        router,
        {
            "coder": "coder",
            "end": END
        }
    )

    return workflow.compile()
