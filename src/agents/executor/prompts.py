from core.errors import MissingPlanError
from core.settings import settings
from models.agents import (
    LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR,
    Agents,
    get_agent_descriptions,
)
from models.prompts import PromptRole
from models.state import State
from prompt_management.registry import get_compiled_prompt_from_registry


def format_agent_list_for_execution(enabled_agents: list[Agents]) -> str:
    """Format agent descriptions for the execution system prompt."""
    enabled_agents = [_agent for _agent in enabled_agents if _agent in LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR]
    return f"`{{{', '.join(sorted(set(enabled_agents)))}}}"


def format_agent_guidelines_for_execution(enabled_agents: list[Agents]) -> str:
    """Format agent usage guidelines for the executor prompt."""
    descriptions = get_agent_descriptions()
    enabled_agents = [_agent for _agent in enabled_agents if _agent in LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR]
    guidelines = []

    if Agents.WEB_RESEARCHER in enabled_agents:
        web_desc = descriptions[Agents.WEB_RESEARCHER]
        guidelines.append(f"- Use `{Agents.WEB_RESEARCHER.value}` when {web_desc.use_when.lower()}.")

    return "\n".join(guidelines)


def executor_system_prompt(enabled_agents: list[Agents]) -> str:
    """Build a system prompt for the Executor to return a specific agent instruction.

    Uses only the prompt registry. A missing or misconfigured prompt is treated as an error.
    """
    agent_list = format_agent_list_for_execution(enabled_agents)
    agent_guidelines = format_agent_guidelines_for_execution(enabled_agents)
    prompt_params = {
        "agent_list": agent_list,
        "agent_guidelines": agent_guidelines,
        "max_replans": settings.max_replans,
    }

    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.executor,
        prompt_params=prompt_params,
        role=PromptRole.SYSTEM,
    )


def executor_user_prompt(state: State) -> str:
    """Build the user prompt for the Executor to return a specific agent instruction.

    Uses only the prompt registry. A missing or misconfigured prompt is treated as an error.
    """
    # Get the replan attempts for the current step, if available. Otherwise sets it to 0.
    attempts = (state.replan_attempts or {}).get(state.current_step, 0)
    messages_tail = state.messages[-4:]
    plan = state.plan
    if plan is None:
        raise MissingPlanError

    current_step_agent = plan.get_step(step_id=state.current_step).instruction.agent
    next_step_agent = plan.get_step(step_id=state.current_step)

    prompt_params = {
        "user_query": state.user_query,
        "current_step": state.current_step,
        "plan": str(plan),
        "replan_flag": state.replan_flag,
        "messages_tail": str(messages_tail),
        "attempts": attempts,
        "max_replans": settings.max_replans,
        "planner_agent": Agents.PLANNER,
        "next_step_agent": next_step_agent,
        "current_step_agent": current_step_agent,
        "web_researcher_agent": Agents.WEB_RESEARCHER,
    }


    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.executor,
        prompt_params=prompt_params,
        role=PromptRole.USER_PLAN,
    )
