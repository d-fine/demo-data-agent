from __future__ import annotations

from pydantic_ai import Agent

from agents.visualizer.prompts import visualizer_system_prompt
from agents.visualizer.tools import run_matplotlib
from core.settings import settings
from models.state import Message, State

visualizer = Agent(
    model=f"openai:{settings.openai.visualizer_llm}",
    tools=[run_matplotlib],
    deps_type=State,
    output_type=Message,
)


@visualizer.system_prompt
async def add_system_prompt() -> str | None:
    """Create and add visualizer system prompt to Visualizer agent."""
    return visualizer_system_prompt()
