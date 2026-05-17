# ruff: noqa: S101

from unittest.mock import MagicMock, patch

from agents.synthesizer.prompts import synthesizer_system_prompt, synthesizer_user_prompt
from core.settings import AgentSettings
from models.prompts import PromptRole
from models.state import State


@patch("agents.synthesizer.prompts.get_compiled_prompt_from_registry")
def test_get_synthesizer_system_prompt(mock_compiled_prompt: MagicMock, mock_settings: AgentSettings) -> None:
    """Validate if compiling of synthesizer_system_prompt is working as expected."""
    prompt = "This is a mock synthesizer system prompt."
    mock_compiled_prompt.return_value = prompt

    result = synthesizer_system_prompt()

    assert result == prompt
    mock_compiled_prompt.assert_called_once_with(
        prompt_config=mock_settings.prompt_registry.synthesizer,
        prompt_params=None,
        role=PromptRole.SYSTEM,
    )


@patch("agents.synthesizer.prompts.get_compiled_prompt_from_registry")
def test_call_synthesizer_node_user_prompt_generation(
    mock_compiled_prompt: MagicMock, mock_settings: AgentSettings, mock_state: State
) -> None:
    """Validate correct prompt param construction for synthesizer user prompt."""
    prompt = "This is a mock synthesizer user prompt."
    mock_compiled_prompt.return_value = prompt

    result = synthesizer_user_prompt(mock_state)

    assert result == prompt

    expected_context = "Web research result 1.\n\n---\n\nWeb research result 2."

    mock_compiled_prompt.assert_called_once_with(
        prompt_config=mock_settings.prompt_registry.synthesizer,
        prompt_params={
            "user_query": mock_state.user_query,
            "context": expected_context,
        },
        role=PromptRole.USER_PLAN,
    )
