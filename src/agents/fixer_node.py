from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AuditingState
from src.agents.utils import extract_text

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

_FIXER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an Expert Python Developer. Refactor the original code to "
     "resolve the Auditor's feedback and fix any linting errors. Output "
     "ONLY raw, valid Python code. Do not include markdown formatting "
     "like ```python or ```."),
    ("human",
     "Original Code:\n{original}\n\n"
     "Auditor Feedback:\n{feedback}\n\n"
     "Linting Errors:\n{errors}\n\n"
     "Please provide the fully refactored function."),
])


def fixer_node(state: AuditingState) -> dict:
    """
    The Coder: reads original_code, feedback_history, and linting_errors,
    writes a new refactored_code, and bumps iteration_count by 1.
    """
    original = state["original_code"]
    feedback = "\n".join(state["feedback_history"])
    errors = state.get("linting_errors") or "No errors yet."
    current_iterations = state.get("iteration_count", 0)

    chain = _FIXER_PROMPT | llm
    response = chain.invoke({
        "original": original,
        "feedback": feedback,
        "errors": errors,
    })
    fixed_code = extract_text(response.content).strip()

    return {
        "refactored_code": fixed_code,
        "linting_errors": None,  # reset — the Tester will re-check next
        "iteration_count": current_iterations + 1,
    }