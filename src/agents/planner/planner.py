from langfuse import get_client
from pydantic_ai import Agent, RunContext

from agents.planner.prompts import planner_instruction_prompt, planner_system_prompt
from core.settings import settings
from models.state import Plan, State

langfuse_client = get_client()

Agent.instrument_all()

planner = Agent(
    model=f"openai:{settings.openai.planner_llm}",
    deps_type=State,
    output_type=Plan,
    instrument=True,
)


@planner.system_prompt
async def add_system_prompt(ctx: RunContext[State]) -> str | None:
    """Create and add planner system prompt to Planner agent."""
    return planner_system_prompt(enabled_agents=ctx.deps.enabled_agents)


@planner.instructions
async def add_instructions(ctx: RunContext[State]) -> str | None:
    """Create and add planner instructions to Planner agent."""
    return planner_instruction_prompt(enabled_agents=ctx.deps.enabled_agents)
