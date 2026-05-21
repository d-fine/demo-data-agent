from pydantic_ai import Agent

from agents.chart_summarizer.prompts import chart_summarizer_system_prompt
from core.settings import settings
from models.state import Message, State

chart_summarizer = Agent(
    model=f"openai:{settings.openai.chart_summarizer_llm}",
    deps_type=State,
    output_type=Message,
    instrument=True,
)


@chart_summarizer.system_prompt
async def add_system_prompt() -> str | None:
    """Create and add chart summarizer system prompt to Chart summarizer agent."""
    return chart_summarizer_system_prompt()
