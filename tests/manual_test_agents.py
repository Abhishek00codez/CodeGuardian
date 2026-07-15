"""
Manual test — actually calls the Gemini API. Requires:
  - GOOGLE_API_KEY set in your .env file
  - pip install -r requirements.txt already run

Run from project root:
    python -m tests.manual_test_agents
"""

from dotenv import load_dotenv

load_dotenv()  # reads .env and puts GOOGLE_API_KEY into the environment

from pathlib import Path

from src.ingestor import CodeIngestor
from src.agents.auditor_node import auditor_node
from src.agents.fixer_node import fixer_node

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "flawed_script.py"


def main():
    source = DATA_FILE.read_text()
    functions = CodeIngestor.extract_functions(source)

    # Grab the O(n^2) duplicate-finder to run through the Critic and Coder
    state = CodeIngestor.initialize_state(functions["find_duplicates"])

    print("=" * 60)
    print("ORIGINAL CODE")
    print("=" * 60)
    print(state["original_code"])

    print("\n" + "=" * 60)
    print("CALLING CRITIC (auditor_node)...")
    print("=" * 60)
    critic_update = auditor_node(state)
    # Manually merge the update into our local state, same way LangGraph would
    state["feedback_history"] = state["feedback_history"] + critic_update["feedback_history"]
    print(state["feedback_history"][-1])

    print("\n" + "=" * 60)
    print("CALLING CODER (fixer_node)...")
    print("=" * 60)
    fixer_update = fixer_node(state)
    state.update(fixer_update)
    print(state["refactored_code"])

    print("\n" + "=" * 60)
    print(f"iteration_count is now: {state['iteration_count']}")
    print("=" * 60)


if __name__ == "__main__":
    main()