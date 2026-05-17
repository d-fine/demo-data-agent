from core.settings import settings
from models.prompts import PromptRole
from prompt_management.registry import get_compiled_prompt_from_registry


def web_researcher_system_prompt() -> str | None:
    """Build the system prompt for the Web-Researcher to return a web-research result.

    Uses only the prompt registry.
    """
    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.web_researcher,
        prompt_params=None,
        role=PromptRole.SYSTEM,
    )
