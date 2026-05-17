from core.settings import settings
from models.agents import Agents
from models.prompts import PromptRole
from models.state import State
from prompt_management.registry import get_compiled_prompt_from_registry


def visualizer_system_prompt() -> str | None:
    """Build the system prompt for the Visualizer to return a visualized result.

    Uses only the prompt registry.
    """
    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.visualizer,
        prompt_params=None,
        role=PromptRole.SYSTEM,
    )


def visualizer_user_prompt(state: State) -> str | None:
    """Build the user prompt for the Visualizer to return the final result."""
    relevant_messages: list[str] = [
        _msg.content for _msg in state.messages if _msg.creator in (Agents.PLANNER, Agents.WEB_RESEARCHER)
    ]
    context = "\n\n---\n\n".join(relevant_messages)

    prompt_params = {
        "user_query": state.user_query,
        "context": context,
    }

    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.visualizer,
        prompt_params=prompt_params,
        role=PromptRole.USER_PLAN,
    )
