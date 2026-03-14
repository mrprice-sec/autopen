"""
Summariser — trims tool output before feeding back to the ReAct agent.
Prevents context window overflow on llama3.2:3b.
"""

MAX_CHARS = 2000  # ~500 tokens


def summarise(output: str, tool_name: str = "") -> str:
    """
    Trims tool output to MAX_CHARS.
    Keeps the beginning and end of output (most useful parts).
    """
    if not output or not output.strip():
        return f"[{tool_name}] No output returned."

    output = output.strip()

    if len(output) <= MAX_CHARS:
        return output

    half = MAX_CHARS // 2
    trimmed = (
        output[:half]
        + f"\n\n... [output trimmed, {len(output)} chars total] ...\n\n"
        + output[-half:]
    )
    return trimmed
