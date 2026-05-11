from agents.common.prompts import common_system_prompt
from models.agents import Agents
from models.state import State


def synthesizer_system_prompt() -> str:
    """Build the system prompt for the Synthesizer to return a synthesized result."""
    specific_sytem_prompt = """
You are the **Synthesizer**. Use the context below to directly answer the user's question.
Perform any lightweight calculations, comparisons, or inferences required.
Do not invent facts not supported by the context.
If data is missing, say what's missing and, if helpful, offer a clearly labeled best-effort estimate with assumptions.
If you are finished with producing your summary, switch the `is_final` flag to `True` to indicate that the
final response to the user's questions has been produced.

Produce a concise response that fully answers the question, with the following guidance:
- Start with the direct answer (one short paragraph or a tight bullet list).
- Include key figures from any 'Results:' tables (e.g., totals, top items).
- If any message contains citations, include them as a brief 'Citations: [...]' line.
- Keep the output crisp; avoid meta commentary or tool instructions.
"""
    return common_system_prompt + f"\n{specific_sytem_prompt}"


def synthesizer_user_prompt(state: State) -> str:
    """Build the user prompt for the Synthesizer to return the final result."""
    relevant_messages: list[str] = [
        _msg.content
        for _msg in state.messages
        if _msg.creator in (Agents.WEB_RESEARCHER, Agents.VISUALIZER, Agents.CHART_SUMMARIZER)
    ]
    return f"**User question:** {state.user_query}\n\n**Context:**\n\n" + "\n\n---\n\n".join(relevant_messages)
