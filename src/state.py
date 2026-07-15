import operator
from typing import Annotated, List, Optional, TypedDict

class AuditingState(TypedDict):
    original_code: str
    feedback_history: Annotated[List[str], operator.add]
    refactored_code: Optional[str]
    linting_errors: Optional[str]
    iteration_count: int