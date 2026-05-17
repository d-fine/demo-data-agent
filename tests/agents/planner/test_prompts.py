# ruff: noqa: S101
from unittest.mock import MagicMock, patch

import pytest
from dirty_equals import IsStr

from agents.planner.prompts import (
    get_compiled_prompt_from_registry,
    planner_instruction_prompt,
    planner_system_prompt,
    planner_user_prompt,
)
from core.settings import AgentSettings
from models.agents import Agents
from models.prompts import PromptRegistryConfig, PromptRole
from models.state import State


@pytest.fixture
def mock_prompt_config() -> PromptRegistryConfig:
    """Mock prompt registry config for testing purposes."""
    return PromptRegistryConfig(
        name="test_planner_system_prompt",
        type="text",
        label="test_label",
        version=2,
    )


@pytest.fixture
def mock_enabled_agents() -> list[Agents]:
    """Mock list of enabled agents for testing purposes."""
    return [Agents.SYNTHESIZER]


@patch("prompt_management.registry.langfuse_client.get_prompt")
def test_get_compiled_prompt_from_registry_text_prompt_without_params(
    mock_prompt: MagicMock, mock_prompt_config: PromptRegistryConfig
) -> None:
    """Validate if compiling prompt works as expected for text prompt without parameters."""
    prompt = "This is a mock prompt."
    mock_prompt.return_value.prompt = prompt

    result = get_compiled_prompt_from_registry(mock_prompt_config, prompt_params=None, role=None)

    assert result == prompt


@patch("prompt_management.registry.langfuse_client.get_prompt")
def test_get_compiled_prompt_from_registry_text_prompt_with_params(
    mock_prompt: MagicMock, mock_prompt_config: PromptRegistryConfig
) -> None:
    """Validate if compiling prompt works as expected for text prompt without parameters."""
    prompt = "This is a mock prompt with parameter '{value}'."
    params = {"value": "test_value"}
    mock_prompt.return_value.prompt = prompt

    result = get_compiled_prompt_from_registry(mock_prompt_config, prompt_params=params, role=None)

    assert result == "This is a mock prompt with parameter 'test_value'."


@patch("prompt_management.registry.langfuse_client.get_prompt")
def test_get_compiled_prompt_from_registry_chat_prompt_without_params(
    mock_prompt: MagicMock, mock_prompt_config: PromptRegistryConfig
) -> None:
    """Validate if compiling prompt works as expected for text prompt without parameters."""
    mock_prompt_config.type = "chat"
    prompt = [
        {"role": PromptRole.SYSTEM, "content": "This is a test system prompt"},
        {"role": PromptRole.USER_PLAN, "content": "This is a test user prompt."},
    ]
    mock_prompt.return_value.prompt = prompt

    result = get_compiled_prompt_from_registry(mock_prompt_config, prompt_params=None, role=PromptRole.SYSTEM)

    assert result == "This is a test system prompt"


@patch("prompt_management.registry.langfuse_client.get_prompt")
def test_get_compiled_prompt_from_registry_chat_prompt_with_wrong_chat_prompt_format(
    mock_prompt: MagicMock, mock_prompt_config: PromptRegistryConfig
) -> None:
    """Validate if compiling prompt works as expected for text prompt without parameters."""
    mock_prompt_config.type = "chat"
    prompt = {PromptRole.SYSTEM: "This is a test system role."}
    mock_prompt.return_value.prompt = prompt

    expected_error_msg = "Received prompt from the Prompt registry is not a chat prompt."
    with pytest.raises(ValueError, match=expected_error_msg):
        _ = get_compiled_prompt_from_registry(mock_prompt_config, prompt_params=None, role=PromptRole.SYSTEM)


@patch("prompt_management.registry.langfuse_client.get_prompt")
def test_get_compiled_prompt_from_registry_chat_prompt_not_available_for_role(
    mock_prompt: MagicMock, mock_prompt_config: PromptRegistryConfig
) -> None:
    """Validate if compiling prompt works as expected for text prompt without parameters."""
    mock_prompt_config.type = "chat"
    prompt = [
        {"role": PromptRole.SYSTEM, "content": "This is a test system prompt"},
        {"role": PromptRole.USER_PLAN, "content": "This is a test user prompt."},
    ]
    mock_prompt.return_value.prompt = prompt

    result = get_compiled_prompt_from_registry(mock_prompt_config, prompt_params=None, role=PromptRole.INSTRUCTIONS)

    assert result is None


@patch("agents.planner.prompts.get_compiled_prompt_from_registry")
def test_get_planner_system_prompt(
    mock_compiled_prompt: MagicMock, mock_settings: AgentSettings, mock_enabled_agents: list[Agents]
) -> None:
    """Validate if compiling of planner_system_prompt is working as expected."""
    prompt = "This is a mock system prompt."
    mock_compiled_prompt.return_value = prompt

    result = planner_system_prompt(enabled_agents=mock_enabled_agents)

    assert result == prompt
    mock_compiled_prompt.assert_called_once_with(
        prompt_config=mock_settings.prompt_registry.planner,
        prompt_params={
            "agent_list": IsStr(),
            "agent_guidelines": IsStr(),
        },
        role=PromptRole.SYSTEM,
    )


@patch("agents.planner.prompts.get_compiled_prompt_from_registry")
def test_get_planner_instructions(
    mock_compiled_prompt: MagicMock, mock_settings: AgentSettings, mock_enabled_agents: list[Agents]
) -> None:
    """Validate if compiling of planner_instruction is working as expected."""
    prompt = "This is a mock instruction."
    mock_compiled_prompt.return_value = prompt

    result = planner_instruction_prompt(enabled_agents=mock_enabled_agents)

    assert result == prompt
    mock_compiled_prompt.assert_called_once_with(
        prompt_config=mock_settings.prompt_registry.planner,
        prompt_params={
            "agent_list": IsStr(),
            "agent_guidelines": IsStr(),
        },
        role=PromptRole.INSTRUCTIONS,
    )


@patch("agents.planner.prompts.get_compiled_prompt_from_registry")
def test_get_planner_user_prompt_plan(
    mock_compiled_prompt: MagicMock, mock_settings: AgentSettings, mock_state: State
) -> None:
    """Validate if compiling of planner_user_prompt (plan) is working as expected."""
    prompt = "This is a mock user prompt."
    mock_compiled_prompt.return_value = prompt

    result = planner_user_prompt(state=mock_state)

    assert result == prompt
    mock_compiled_prompt.assert_called_once_with(
        prompt_config=mock_settings.prompt_registry.planner,
        prompt_params={"user_query": mock_state.user_query},
        role=PromptRole.USER_PLAN,
    )


@patch("agents.planner.prompts.get_compiled_prompt_from_registry")
def test_get_planner_user_prompt_replan(
    mock_compiled_prompt: MagicMock, mock_settings: AgentSettings, mock_state: State
) -> None:
    """Validate if compiling of planner_user_prompt (replan) is working as expected."""
    prompt = "This is a mock user prompt."
    mock_compiled_prompt.return_value = prompt
    mock_state.replan_flag = True

    result = planner_user_prompt(state=mock_state)

    assert result == prompt
    mock_compiled_prompt.assert_called_once_with(
        prompt_config=mock_settings.prompt_registry.planner,
        prompt_params={"user_query": mock_state.user_query, "replan_reason": "", "current_plan": IsStr()},
        role=PromptRole.USER_REPLAN,
    )
