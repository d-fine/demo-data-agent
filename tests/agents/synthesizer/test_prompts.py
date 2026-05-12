# ruff: noqa: S101

from agents.synthesizer.prompts import synthesizer_user_prompt
from models.state import State


def test_call_synthesizer_node_user_prompt_generation(mock_state: State) -> None:
    """Validate correct error raising in case of incorrect LLM return format."""
    result = synthesizer_user_prompt(mock_state)

    expected_query = (
        f"**User question:** {mock_state.user_query}\n\n"
        "**Context:**\n\nWeb research result 1.\n\n---\n\nWeb research result 2."
    )
    assert result == expected_query
