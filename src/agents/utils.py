def extract_text(content) -> str:
    """
    Normalizes an LLM response's .content into a plain string.

    Most models return .content as a plain string. Some newer 'thinking'
    models (e.g. Gemini 3.x) return it as a list of content blocks instead,
    e.g. [{'type': 'text', 'text': '...', 'extras': {'signature': '...'}}].
    This extracts and joins just the text portions, regardless of format.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)

    return str(content)