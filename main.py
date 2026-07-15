from dotenv import load_dotenv

load_dotenv()  # must run before importing anything that builds an LLM client

from pathlib import Path

from src.ingestor import CodeIngestor
from src.workflow import auditing_graph

DATA_FILE = Path(__file__).resolve().parent / "data" / "flawed_script.py"

# Which function from flawed_script.py to run through the pipeline.
TARGET_FUNCTION = "find_duplicates"


def main():
    source = DATA_FILE.read_text()
    functions = CodeIngestor.extract_functions(source)

    if TARGET_FUNCTION not in functions:
        raise ValueError(f"'{TARGET_FUNCTION}' not found in {DATA_FILE}")

    initial_state = CodeIngestor.initialize_state(functions[TARGET_FUNCTION])

    print("=" * 70)
    print(f"STARTING GRAPH for function: {TARGET_FUNCTION}")
    print("=" * 70)

    final_state = None

    # .stream() yields a dict after each node finishes, keyed by node name.
    # This lets us watch the state mutate step by step, including any
    # retry loop, instead of only seeing the final result.
    for step in auditing_graph.stream(initial_state):
        for node_name, node_output in step.items():
            print(f"\n--- NODE COMPLETED: {node_name} ---")
            if node_name == "auditor":
                print("Latest feedback:\n", node_output["feedback_history"][-1][:300], "...")
            elif node_name == "fixer":
                print(f"iteration_count -> {node_output['iteration_count']}")
                print("refactored_code (first 200 chars):\n", node_output["refactored_code"][:200])
            elif node_name == "tester":
                status = "PASS" if node_output["linting_errors"] is None else "FAIL"
                print(f"Tester result: {status}")
                if status == "FAIL":
                    print("Error:", node_output["linting_errors"])
            final_state = node_output

    print("\n" + "=" * 70)
    print("GRAPH FINISHED")
    print("=" * 70)
    print("Final iteration_count:", final_state.get("iteration_count"))
    print("Final linting_errors:", final_state.get("linting_errors"))
    print("\nFinal refactored_code:\n")
    print(final_state.get("refactored_code"))


if __name__ == "__main__":
    main()