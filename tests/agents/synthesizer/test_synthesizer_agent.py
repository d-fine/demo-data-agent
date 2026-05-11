# ruff: noqa: S101
from datetime import UTC
from unittest.mock import MagicMock, patch

import pytest
from dirty_equals import IsInt, IsNow, IsStr
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

from agents import synthesizer
from models.state import Message


@pytest.mark.asyncio
@patch("agents.synthesizer.synthesizer.synthesizer_system_prompt")
async def test_call_executor(mock_system_prompt: MagicMock) -> None:
    """Validate if synthesizer can be correctly called and returns an output of type Message."""
    mock_system_prompt.return_value = "This is a test system prompt."

    with capture_run_messages() as messages, synthesizer.override(model=TestModel()):
        prompt = "What is tomorrow's date?"
        response = await synthesizer.run(user_prompt=prompt)

    output = response.output
    assert isinstance(output, Message)
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
                ToolCallPart(
                    tool_name="final_result",
                    args={"content": IsStr()},
                    tool_call_id=IsStr(),
                ),
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
