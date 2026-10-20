from src.parser import parse_code

def test_parse_valid_code():
    code = """
class MyClass:
    def __init__(self):
        pass

def my_func(a, b):
    if a > b:
        return a
    return b
"""
    res = parse_code(code)
    assert res["status"] == "success"
    ctx = res["ast_context"]
    assert len(ctx["classes"]) == 1
    assert ctx["classes"][0]["name"] == "MyClass"
    assert len(ctx["functions"]) == 2
    func_names = [f["name"] for f in ctx["functions"]]
    assert "__init__" in func_names
    assert "my_func" in func_names

def test_parse_syntax_error():
    code = "def my_func(a, b) return a"
    res = parse_code(code)
    assert res["status"] == "error"
    assert "syntax_error" in res
