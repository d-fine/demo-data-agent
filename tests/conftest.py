import os

import pytest
from pydantic_ai import models

from core.settings import AgentSettings
from models.prompts import PromptRegistryConfig

models.ALLOW_MODEL_REQUESTS = False
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("TAVILY_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def mock_settings() -> AgentSettings:
    """Initialize mock agent settings for testing purposes."""
    from core.settings import settings  # noqa: PLC0415

    settings.prompt_registry.planner = PromptRegistryConfig(name="mock_planner_prompt")
    return settings
