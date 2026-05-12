from agents.common.prompts import common_system_prompt
from models.agents import Agents
from models.state import State


def visualizer_system_prompt() -> str:
    """Build the system prompt for the Visualizer to return a visualized result."""
    specific_sytem_prompt = """
        You are the Chart Generator in a multi-Agent system.
        - When the user asks for a chart, you MUST call the 'run_matplotlib' tool.
        - The 'code' argument must be valid Python that uses the provided 'plt' and 'ax'
        to fully define the plot. Do NOT include imports or figure creation.
        - The 'filename' argument should be a short, snake_case description ending with '.png',
        e.g. 'revenue_per_quarter.png'.
        - After the tool returns, briefly describe the chart and INCLUDE the file path in your answer.
        - At the very end of your message, output EXACTLY two lines so the summarizer can find them:
           - FILE_PATH: <relative_path_to_chart_file>
           - CHART_NOTES: <one concise sentence summarizing the main insight in the chart>
        Do not include any other trailing text after these two lines.
"""
    return common_system_prompt + f"\n{specific_sytem_prompt}"


def visualizer_user_prompt(state: State) -> str:
    """Build the user prompt for the Visualizer to return the final result."""
    relevant_messages: list[str] = [
        _msg.content for _msg in state.messages if _msg.creator in (Agents.PLANNER, Agents.WEB_RESEARCHER)
    ]
    return f"**User question:** {state.user_query}\n\n**Context:**\n\n" + "\n\n---\n\n".join(relevant_messages)
