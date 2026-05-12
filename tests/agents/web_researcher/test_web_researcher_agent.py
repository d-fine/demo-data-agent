# ruff: noqa: S101
from datetime import UTC
from unittest.mock import AsyncMock, MagicMock, patch

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

from agents import web_researcher
from models.state import Message


@pytest.mark.asyncio
@patch("tavily.async_tavily.AsyncTavilyClient.search", new_callable=AsyncMock)
@patch("agents.web_researcher.web_researcher.web_researcher_system_prompt")
async def test_call_executor(mock_system_prompt: MagicMock, mock_search: MagicMock) -> None:
    """Validate if web researcher can be correctly called and returns an output of type Message."""
    mock_system_prompt.return_value = "This is a test system prompt."
    mock_search.return_value = {
        "results": [
            {
                "url": "https://example.com",
                "title": "Example",
                "content": "Example search result content.",
                "score": 1,
            }
        ]
    }

    with capture_run_messages() as messages, web_researcher.override(model=TestModel()):
        prompt = "What is tomorrow's date?"
        response = await web_researcher.run(user_prompt=prompt)

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
                    tool_name="tavily_search",
                    args={"query": IsStr()},
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
                ToolReturnPart(
                    tool_name="tavily_search", content=IsInstance(list), tool_call_id=IsStr(), timestamp=IsNow(tz=UTC)
                )
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
