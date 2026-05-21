from pydantic_ai import Agent

from agents.synthesizer.prompts import synthesizer_system_prompt
from core.settings import settings
from models.state import Message, State

synthesizer = Agent(
    model=f"openai:{settings.openai.synthesizer_llm}",
    deps_type=State,
    output_type=Message,
    instrument=True,
)


@synthesizer.system_prompt
async def add_system_prompt() -> str | None:
    """Create and add synthesizer system prompt to Synthesizer agent."""
    return synthesizer_system_prompt()
