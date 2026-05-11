# ruff: noqa: S101
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai import AgentRunResult
from pydantic_graph import GraphRunContext

from agents import ExecutorNode, PlannerNode, SynthesizerNode, WebResearchNode
from models.agents import Agents
from models.state import DetailedAgentInstruction, Message, State


@pytest.fixture
def detailed_agent_instruction() -> DetailedAgentInstruction:
    """Initialize detailed agent instruction for testing purposes."""
    return DetailedAgentInstruction(
        replan=False,
        goto=Agents.WEB_RESEARCHER,
        reason="Resonable action stated by plan.",
        query="Web research instruction.",
    )


@pytest.fixture
def agent_result(detailed_agent_instruction: DetailedAgentInstruction) -> AgentRunResult[DetailedAgentInstruction]:
    """Initialize agent result for testing purposes."""
    return AgentRunResult(output=detailed_agent_instruction)


@patch("agents.executor.executor_node.executor_user_prompt")
@patch("agents.executor.executor_node.executor.run")
@pytest.mark.asyncio
async def test_call_executor_node_following_plan(
    mock_llm_response: AsyncMock,
    mock_user_prompt: MagicMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[DetailedAgentInstruction],
) -> None:
    """Validate successful executor node call when following the plan."""
    mock_llm_response.return_value = agent_result
    mock_user_prompt.return_value = "Create a detailed agent instruction."
    step = mock_context.state.current_step

    executor_node = ExecutorNode()
    result = await executor_node.run(mock_context)

    assert isinstance(result, WebResearchNode)
    assert mock_context.state.messages[-1] == Message(
        creator=Agents.EXECUTOR, content=agent_result.output.model_dump_json()
    )
    assert mock_context.state.last_reason == agent_result.output.reason
    assert mock_context.state.agent_query == agent_result.output.query
    assert mock_context.state.replan_flag == agent_result.output.replan
    assert mock_context.state.current_step == step + 1


@patch("agents.executor.executor_node.executor_user_prompt")
@patch("agents.executor.executor_node.executor.run")
@pytest.mark.asyncio
async def test_call_executor_node_not_following_plan(
    mock_llm_response: AsyncMock,
    mock_user_prompt: MagicMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[DetailedAgentInstruction],
) -> None:
    """Validate successful executor node call when not following the plan."""
    agent_result.output.goto = Agents.SYNTHESIZER

    mock_llm_response.return_value = agent_result
    mock_user_prompt.return_value = "Create a detailed agent instruction."
    step = mock_context.state.current_step

    executor_node = ExecutorNode()
    result = await executor_node.run(mock_context)

    assert isinstance(result, SynthesizerNode)
    assert mock_context.state.messages[-1] == Message(
        creator=Agents.EXECUTOR, content=agent_result.output.model_dump_json()
    )
    assert mock_context.state.last_reason == agent_result.output.reason
    assert mock_context.state.agent_query == agent_result.output.query
    assert mock_context.state.replan_flag == agent_result.output.replan
    assert mock_context.state.current_step == step


@pytest.mark.skip(reason="Difference result local vs. in CI/CD.")
@patch("agents.executor.executor_node.executor_user_prompt")
@patch("agents.executor.executor_node.executor.run")
@pytest.mark.asyncio
async def test_call_executor_node_prepare_for_replanning(
    mock_llm_response: AsyncMock,
    mock_user_prompt: MagicMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[DetailedAgentInstruction],
) -> None:
    """Validate successful executor node call when executor decided to replan."""
    agent_result.output.replan = True
    agent_result.output.goto = Agents.PLANNER

    mock_llm_response.return_value = agent_result
    mock_user_prompt.return_value = "Create a detailed agent instruction."
    step = mock_context.state.current_step

    executor_node = ExecutorNode()
    result = await executor_node.run(mock_context)

    assert isinstance(result, PlannerNode)
    assert mock_context.state.messages[-1] == Message(
        creator=Agents.EXECUTOR, content=agent_result.output.model_dump_json()
    )
    assert mock_context.state.last_reason == agent_result.output.reason
    assert mock_context.state.agent_query == agent_result.output.query
    assert mock_context.state.replan_flag == agent_result.output.replan
    assert mock_context.state.current_step == step


@pytest.mark.asyncio
async def test_call_executor_node_after_replanning(
    mock_context: GraphRunContext[State, None],
) -> None:
    """Validate successful executor node call directly after replanning."""
    mock_context.state.replan_flag = True

    step = mock_context.state.current_step
    step_instruction = mock_context.state.plan.get_step(step_id=step).instruction  # ty:ignore[possibly-missing-attribute]
    expected_output = DetailedAgentInstruction(
        replan=False,
        goto=step_instruction.agent,
        reason="Following the suggested plan after replanning.",
        query=step_instruction.action,
    )

    executor_node = ExecutorNode()
    result = await executor_node.run(mock_context)

    assert isinstance(result, WebResearchNode)
    assert mock_context.state.messages[-1] == Message(
        creator=Agents.EXECUTOR, content=expected_output.model_dump_json()
    )
    assert mock_context.state.last_reason == expected_output.reason
    assert mock_context.state.agent_query == expected_output.query
    assert mock_context.state.replan_flag == expected_output.replan
    assert mock_context.state.current_step == step + 1
