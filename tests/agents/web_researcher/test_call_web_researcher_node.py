# ruff: noqa: S101
from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest
from pydantic_ai import AgentRunResult
from pydantic_graph import GraphRunContext

from agents import ExecutorNode, WebResearchNode
from core.errors import OutputFormatError
from models.agents import Agents
from models.state import Message, State


@pytest.fixture
def agent_result() -> AgentRunResult[Message]:
    """Initialize agent result for testing purposes."""
    return AgentRunResult(output=Message(creator=Agents.WEB_RESEARCHER, content="Test web researcher result."))


@patch("agents.web_researcher.web_researcher_node.web_researcher.run")
@pytest.mark.asyncio
async def test_call_web_researcher(
    mock_llm_response: AsyncMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[Message],
) -> None:
    """Validate successful web researcher node call."""
    mock_llm_response.return_value = agent_result

    web_researcher_node = WebResearchNode()
    result = await web_researcher_node.run(mock_context)

    assert isinstance(result, ExecutorNode)
    assert mock_context.state.messages[-1] == agent_result.output


@patch("agents.web_researcher.web_researcher_node.web_researcher.run")
@pytest.mark.asyncio
async def test_call_web_researcher_update_creator(
    mock_llm_response: AsyncMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[Message],
) -> None:
    """Validate successful web researcher node call, when LLM response contains wrong creator."""
    updated_agent_result = deepcopy(agent_result)
    updated_agent_result.output.creator = Agents.PLANNER
    mock_llm_response.return_value = updated_agent_result

    web_researcher_node = WebResearchNode()
    result = await web_researcher_node.run(mock_context)

    assert isinstance(result, ExecutorNode)
    assert mock_context.state.messages[-1] == agent_result.output


@patch("agents.web_researcher.web_researcher_node.web_researcher.run")
@pytest.mark.asyncio
async def test_call_web_researcher_node_wrong_response_format(
    mock_llm_response: AsyncMock, mock_context: GraphRunContext[State, None]
) -> None:
    """Validate correct error raising in case of incorrect LLM return format."""
    mock_llm_response.return_value = AgentRunResult(output={"name": "TEST", "content": "Incorrect return format."})
    expected_err_msg = OutputFormatError(value=mock_llm_response.return_value.output).message

    web_researcher_node = WebResearchNode()
    with pytest.raises(OutputFormatError, match=expected_err_msg):
        await web_researcher_node.run(mock_context)
