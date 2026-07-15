from pathlib import Path
from src.ingestor import CodeIngestor
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "flawed_script.py"

def test_extract_functions_finds_both_functions():
    source = DATA_FILE.read_text()
    functions = CodeIngestor.extract_functions(source)
    assert "find_duplicates" in functions
    assert "load_config" in functions
    assert "def find_duplicates(items):" in functions["find_duplicates"]
    assert "eval(contents)" in functions["load_config"]

def test_initialize_state_shape():
    state = CodeIngestor.initialize_state("def foo(): pass")
    assert state["original_code"] == "def foo(): pass"
    assert state["feedback_history"] == []
    assert state["refactored_code"] is None
    assert state["linting_errors"] is None
    assert state["iteration_count"] == 0

if __name__ == "__main__":
    # Quick manual run without pytest, so you can just do:
    # python tests/test_ingestor.py
    source = DATA_FILE.read_text()
    functions = CodeIngestor.extract_functions(source)
    print(f"Found {len(functions)} function(s):\n")
    for name, code in functions.items():
        print(f"--- {name} ---")
        print(code)
        print()
    state = CodeIngestor.initialize_state(functions["find_duplicates"])
    print("Initial state for 'find_duplicates':")
    print(state)