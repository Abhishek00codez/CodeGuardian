import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

def get_llm():
    # Use gemini-2.0-flash as it's the standard for general tasks, but fallback to gemini-1.5-pro if unavailable
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

def critic_agent(source_code: str, ast_context: dict) -> str:
    llm = get_llm()
    prompt = f"""
    Analyze the following Python source code for bugs, anti-patterns, and readability issues.
    Consider the AST context provided: {ast_context}

    Code:
    ```python
    {source_code}
    ```

    Provide specific, targeted feedback for improvement. Do not include excessive explanations, just the critique.
    """
    res = llm.invoke([
        SystemMessage(content="You are an expert Python code reviewer. Be concise and accurate."),
        HumanMessage(content=prompt)
    ])
    return res.content

def coder_agent(source_code: str, feedback: str, test_output: str = "") -> str:
    llm = get_llm()
    prompt = f"""
    Refactor the following Python source code based on the feedback provided.

    Code:
    ```python
    {source_code}
    ```

    Feedback/Critique:
    {feedback}
    """

    if test_output:
        prompt += f"\n\nThe code previously failed tests with this output. Fix the errors:\n{test_output}"

    prompt += "\n\nOutput ONLY the complete refactored Python code block. No explanations, no markdown wrapper other than ```python...```."

    res = llm.invoke([
        SystemMessage(content="You are an expert Python coder. Output only the requested code."),
        HumanMessage(content=prompt)
    ])

    # Extract code from markdown if present
    content = res.content.strip()
    if content.startswith("```python"):
        content = content[len("```python"):]
    if content.startswith("```"):
         content = content[len("```"):]
    if content.endswith("```"):
        content = content[:-3]

    return content.strip()
