from src.state import AuditingState

# Hard cap on self-correction attempts. Prevents infinite loops if the LLM
# can't produce valid code after several tries.
MAX_ITERATIONS = 3


def local_tester(state: AuditingState) -> dict:
    """
    The Tester: deterministic, no AI. Tries to compile refactored_code.

    On success -> clears linting_errors (signals "pass" to the router).
    On failure -> stores the exact error message in linting_errors
                  (the Fixer node reads this on its next run).
    """
    code_to_test = state["refactored_code"]

    try:
        compile(code_to_test, filename="<refactored_code>", mode="exec")
        return {"linting_errors": None}
    except SyntaxError as e:
        error_message = f"SyntaxError: {e.msg} (line {e.lineno}, col {e.offset})"
        return {"linting_errors": error_message}


def route_after_test(state: AuditingState) -> str:
    """
    Conditional edge logic (used in Phase 4's graph wiring).
    Decides where the graph goes next based on the Tester's result.
    """
    passed = state["linting_errors"] is None
    hit_iteration_cap = state["iteration_count"] >= MAX_ITERATIONS

    if passed:
        return "pass"
    if hit_iteration_cap:
        return "pass"
    return "retry"