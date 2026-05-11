# ruff: noqa: S101

from datetime import UTC
from unittest.mock import MagicMock, patch

import pytest
from dirty_equals import IsInstance, IsInt, IsNow, IsStr
from pydantic_ai import (
    ModelRequest,
    ModelResponse,
    RequestUsage,
    SystemPromptPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
    capture_run_messages,
)
from pydantic_ai.models.test import TestModel

from agents import planner
from models.state import Plan, State


@pytest.mark.asyncio
@patch("agents.planner.planner.planner_instruction_prompt")
@patch("agents.planner.planner.planner_system_prompt")
async def test_call_planner(mock_system_prompt: MagicMock, mock_instruction: MagicMock, mock_state: State) -> None:
    """Validate if planner can be correctly called and returns an output of type Plan."""
    mock_system_prompt.return_value = "This is a test system prompt."
    mock_instruction.return_value = None

    with capture_run_messages() as messages, planner.override(model=TestModel()):
        prompt = "What is tomorrow's date?"
        response = await planner.run(user_prompt=prompt, deps=mock_state)

    output = response.output
    assert isinstance(output, Plan)
    assert messages == [
        ModelRequest(
            parts=[
                SystemPromptPart(content=mock_system_prompt.return_value, timestamp=IsNow(tz=UTC)),
                UserPromptPart(content=prompt, timestamp=IsNow(tz=UTC)),
            ],
            timestamp=IsNow(tz=UTC),
            run_id=IsStr(),
        ),
        ModelResponse(
            parts=[
                ToolCallPart(tool_name="final_result", args={"steps": IsInstance(list)}, tool_call_id=IsStr()),
            ],
            usage=RequestUsage(input_tokens=IsInt(), output_tokens=IsInt()),
            model_name="test",
            timestamp=IsNow(tz=UTC),
            run_id=IsStr(),
        ),
        ModelRequest(
            parts=[
                ToolReturnPart(tool_name="final_result", content=IsStr(), tool_call_id=IsStr(), timestamp=IsNow(tz=UTC))
            ],
            timestamp=IsNow(tz=UTC),
            run_id=IsStr(),
        ),
    ]
