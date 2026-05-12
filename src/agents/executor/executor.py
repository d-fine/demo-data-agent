from pydantic_ai import Agent, RunContext

from agents.executor.prompts import executor_system_prompt
from core.settings import settings
from models.state import DetailedAgentInstruction, State

executor = Agent(
    model=f"openai:{settings.openai.executor_llm}",
    deps_type=State,
    output_type=DetailedAgentInstruction,
)


@executor.system_prompt
async def add_system_prompt(ctx: RunContext[State]) -> str:
    """Create and add executor system prompt to Executor agent."""
    return executor_system_prompt(enabled_agents=ctx.deps.enabled_agents)
