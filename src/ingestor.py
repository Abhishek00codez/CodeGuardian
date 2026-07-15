import ast
from typing import Dict, TypedDict, List, Optional

from src.state import AuditingState

class CodeIngestor:

    @staticmethod
    def extract_functions(source_code: str) -> Dict[str, str]:
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code provided: {e}")
        functions_map: Dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_text = ast.get_source_segment(source_code, node)
                if func_text:
                    functions_map[node.name] = func_text

        return functions_map
    
    @classmethod
    def initialize_state(cls, target_function_source: str) -> AuditingState:
        return {
            "original_code": target_function_source,
            "feedback_history": [],
            "refactored_code": None,
            "linting_errors": None,
            "iteration_count": 0
        }