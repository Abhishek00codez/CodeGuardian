from src.execution.local_tester import local_tester, route_after_test, MAX_ITERATIONS


def _base_state(refactored_code: str, iteration_count: int = 1) -> dict:
    return {
        "original_code": "def foo(): pass",
        "feedback_history": [],
        "refactored_code": refactored_code,
        "linting_errors": None,
        "iteration_count": iteration_count,
    }


def test_valid_code_passes():
    state = _base_state("def foo(x):\n    return x + 1")
    result = local_tester(state)
    assert result["linting_errors"] is None


def test_broken_code_fails_with_message():
    state = _base_state("def foo(x)\n    return x + 1")  # missing colon
    result = local_tester(state)
    assert result["linting_errors"] is not None
    assert "SyntaxError" in result["linting_errors"]


def test_route_pass_when_no_errors():
    state = _base_state("def foo(): pass")
    state["linting_errors"] = None
    assert route_after_test(state) == "pass"


def test_route_retry_when_errors_and_under_cap():
    state = _base_state("bad code", iteration_count=1)
    state["linting_errors"] = "SyntaxError: something"
    assert route_after_test(state) == "retry"


def test_route_pass_when_errors_but_cap_hit():
    state = _base_state("bad code", iteration_count=MAX_ITERATIONS)
    state["linting_errors"] = "SyntaxError: something"
    assert route_after_test(state) == "pass"


if __name__ == "__main__":
    # Manual run without pytest
    print("Testing valid code...")
    print(local_tester(_base_state("def foo(x):\n    return x + 1")))

    print("\nTesting broken code (missing colon)...")
    print(local_tester(_base_state("def foo(x)\n    return x + 1")))

    print("\nTesting routing logic...")
    print("pass case:", route_after_test({**_base_state("ok"), "linting_errors": None}))
    print("retry case:", route_after_test({**_base_state("bad", 1), "linting_errors": "err"}))
    print("cap-hit case:", route_after_test({**_base_state("bad", MAX_ITERATIONS), "linting_errors": "err"}))