import argparse
import sys
import json
import difflib
import os
from src.workflow import create_workflow

def generate_diff(original: str, modified: str, filename: str) -> str:
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)

    diff = difflib.unified_diff(
        orig_lines,
        mod_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff)

def main():
    parser = argparse.ArgumentParser(description="CodeGuardian: Stateful Multi-Agent Code Review & Refactoring Engine")
    parser.add_argument("--file", type=str, required=True, help="Path to the target python file")
    parser.add_argument("--test-file", type=str, help="Path to an optional pytest file for validation")
    parser.add_argument("--retries", type=int, default=3, help="Max validation loop retries")
    parser.add_argument("--report", action="store_true", help="Emit a structured JSON report")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: Target file {args.file} not found.")
        sys.exit(1)

    with open(args.file, "r") as f:
        original_code = f.read()

    test_code = ""
    if args.test_file:
        if not os.path.exists(args.test_file):
            print(f"Error: Test file {args.test_file} not found.")
            sys.exit(1)
        with open(args.test_file, "r") as f:
            test_code = f.read()

    app = create_workflow()

    initial_state = {
        "source_code": original_code,
        "test_code": test_code,
        "ast_context": {},
        "review_feedback": "",
        "test_output": "",
        "retry_count": 0,
        "max_retries": args.retries,
        "final_status": ""
    }

    print(f"Running CodeGuardian on {args.file}...")

    final_state = None
    for s in app.stream(initial_state):
        if "ast" in s:
            print("=> AST Parsing Complete")
        if "critic" in s:
            print("=> Critic Review Complete")
        if "coder" in s:
            print("=> Coder Refactoring Applied")
        if "validator" in s:
            print(f"=> Validator Run Complete (Status: {s['validator'].get('final_status')})")
        final_state = s

    if not final_state:
        print("Error: Workflow did not return a state.")
        sys.exit(1)

    # Get the last state correctly whether it's wrapped or unwrapped depending on langgraph version
    state_values = final_state[list(final_state.keys())[0]] if hasattr(final_state, "keys") else final_state

    new_code = state_values.get("source_code", "")

    print("\n--- Unified Diff ---")
    diff = generate_diff(original_code, new_code, os.path.basename(args.file))
    print(diff if diff else "No changes made.")

    if state_values.get("final_status") == "success":
        print("\nSUCCESS: Code passed all validation steps.")
    else:
        print(f"\nFAILED: Code did not pass validation after {state_values.get('retry_count')} retries.")

    if args.report:
        report = {
            "file": args.file,
            "status": state_values.get("final_status"),
            "retries": state_values.get("retry_count"),
            "feedback": state_values.get("review_feedback"),
            "test_output": state_values.get("test_output")
        }
        with open("codeguardian_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("\nReport saved to codeguardian_report.json")

if __name__ == "__main__":
    main()
