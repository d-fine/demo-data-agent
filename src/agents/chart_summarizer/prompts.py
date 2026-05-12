from agents.common.prompts import common_system_prompt
from models.agents import Agents
from models.state import State


def chart_summarizer_system_prompt() -> str:
    """Build the system prompt for the chart summarizer to return a caption for the chart result."""
    specific_sytem_prompt = """
        You can only generate image captions.\n
        You are working with a researcher colleague and a chart generator colleague.\n
        Your task is to generate a standalone, concise summary for the provided chart image saved at a local PATH,
        where the PATH should be and only be provided by your chart generator colleague.\n
        The summary should be no more than 3 sentences and should not mention the chart itself.
    """
    return common_system_prompt + f"\n{specific_sytem_prompt}"


def chart_summarizer_user_prompt(state: State) -> str:
    """Build the user prompt for the chart summarizer to return the final result."""
    relevant_messages: list[str] = [
        _msg.content
        for _msg in state.messages
        if _msg.creator in (Agents.PLANNER, Agents.WEB_RESEARCHER, Agents.VISUALIZER)
    ]
    return f"**User question:** {state.user_query}\n\n**Context:**\n\n" + "\n\n---\n\n".join(relevant_messages)
