from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AuditingState
from src.agents.utils import extract_text

# Note: Gemini 3.x models recommend leaving temperature at its default
# (custom values are known to degrade reasoning quality on these models),
# so we don't set it here.
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

_AUDITOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Senior Security and Performance Auditor. Review the "
     "provided Python code. Identify algorithmic inefficiencies and "
     "security vulnerabilities. Provide a concise, bulleted list of "
     "issues. Do NOT provide fixed code."),
    ("human", "Here is the code to audit:\n\n{code}"),
])


def auditor_node(state: AuditingState) -> dict:
    """
    The Critic: reads original_code, writes a critique, appends it to
    feedback_history. Does not touch any other state field.
    """
    code_to_review = state["original_code"]

    chain = _AUDITOR_PROMPT | llm
    response = chain.invoke({"code": code_to_review})
    critique = extract_text(response.content)

    # Because feedback_history uses the operator.add reducer in AuditingState,
    # LangGraph appends this to the existing list rather than overwriting it.
    return {"feedback_history": [critique]}