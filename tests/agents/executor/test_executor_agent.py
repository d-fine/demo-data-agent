# ruff: noqa: S101
from datetime import UTC
from unittest.mock import MagicMock, patch

import pytest
from dirty_equals import IsEnum, IsInt, IsNow, IsStr
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

from agents import executor
from models.agents import Agents
from models.state import DetailedAgentInstruction, State


@pytest.mark.asyncio
@patch("agents.executor.executor.executor_system_prompt")
async def test_call_executor(mock_system_prompt: MagicMock, mock_state: State) -> None:
    """Validate if executor can be correctly called and returns an output of type DetailedAgentInstruction."""
    mock_system_prompt.return_value = "This is a test system prompt."

    with capture_run_messages() as messages, executor.override(model=TestModel()):
        prompt = "What is tomorrow's date?"
        response = await executor.run(user_prompt=prompt, deps=mock_state)

    output = response.output
    assert isinstance(output, DetailedAgentInstruction)
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
                    args={"replan": False, "goto": IsEnum(Agents), "reason": IsStr(), "query": IsStr()},
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
