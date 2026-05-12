# ruff: noqa: S101
from copy import deepcopy
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai import AgentRunResult
from pydantic_graph import GraphRunContext

from agents import ExecutorNode, PlannerNode
from core.errors import OutputFormatError
from models.agents import Agents
from models.state import Instruction, Message, Plan, PlanType, State, Step


@pytest.fixture
def plan() -> Plan:
    """Initialize plan for testing purposes."""
    return Plan(
        steps=[
            Step(step_id=1, instruction=Instruction(agent=Agents.WEB_RESEARCHER, action="First instruction.")),
            Step(step_id=2, instruction=Instruction(agent=Agents.SYNTHESIZER, action="Second instruction.")),
        ],
        type=PlanType.INITIAL,
    )


@pytest.fixture
def agent_result(plan: Plan) -> AgentRunResult[Plan]:
    """Initialize agent result for testing purposes."""
    return AgentRunResult(output=plan)


@patch("agents.planner.planner_node.planner_user_prompt")
@patch("agents.planner.planner_node.planner.run")
@pytest.mark.asyncio
async def test_call_planner_node(
    mock_llm_response: AsyncMock,
    mock_user_prompt: MagicMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[Plan],
) -> None:
    """Validate successful planner node call."""
    mock_llm_response.return_value = agent_result
    mock_user_prompt.return_value = "Create a plan."

    planner_node = PlannerNode()
    result = await planner_node.run(mock_context)

    assert isinstance(result, ExecutorNode)
    assert mock_context.state.messages[-1] == Message(
        creator=Agents.PLANNER, content=agent_result.output.model_dump_json()
    )
    assert mock_context.state.plan == agent_result.output


@patch("agents.planner.planner_node.planner_user_prompt")
@patch("agents.planner.planner_node.planner.run")
@pytest.mark.asyncio
async def test_call_planner_node_wrong_response_format(
    mock_llm_response: AsyncMock, mock_user_prompt: MagicMock, mock_context: GraphRunContext[State, None]
) -> None:
    """Validate correct error raising in case of incorrect LLM return format."""
    mock_llm_response.return_value = AgentRunResult(output={"name": "TEST", "content": "Incorrect return format."})
    mock_user_prompt.return_value = "Create a plan."
    expected_err_msg = OutputFormatError(value=mock_llm_response.return_value.output).message

    planner = PlannerNode()
    with pytest.raises(OutputFormatError, match=expected_err_msg):
        await planner.run(mock_context)


@patch("agents.planner.planner_node.planner_user_prompt")
@patch("agents.planner.planner_node.planner.run")
@pytest.mark.asyncio
async def test_call_planner_node_plan_type_incorrectly_set_to_replan(
    mock_llm_response: AsyncMock,
    mock_user_prompt: MagicMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[Plan],
) -> None:
    """Validate correct state update if returned plan's type equals 'REPLAN', while state's replan_flag is 'false'."""
    expected_plan = deepcopy(agent_result.output)
    agent_result.output.type = PlanType.REPLAN
    mock_llm_response.return_value = agent_result
    mock_user_prompt.return_value = "Create a plan."

    planner = PlannerNode()
    _ = await planner.run(mock_context)

    assert mock_context.state.plan == expected_plan
    assert mock_context.state.messages[-1] == Message(creator=Agents.PLANNER, content=expected_plan.model_dump_json())


@patch("agents.planner.planner_node.planner_user_prompt")
@patch("agents.planner.planner_node.planner.run")
@pytest.mark.asyncio
async def test_call_planner_node_plan_type_incorrectly_set_to_initial(
    mock_llm_response: AsyncMock,
    mock_user_prompt: MagicMock,
    mock_context: GraphRunContext[State, None],
    agent_result: AgentRunResult[Plan],
) -> None:
    """Validate correct state update if returned plan's type equals 'INITIAL', while state's replan_flag is 'true'."""
    mock_context.state.replan_flag = True
    mock_llm_response.return_value = agent_result
    mock_user_prompt.return_value = "Create a plan."

    planner = PlannerNode()
    _ = await planner.run(mock_context)

    expected_plan = deepcopy(agent_result.output)
    expected_plan.type = PlanType.REPLAN
    assert mock_context.state.plan == expected_plan
    assert mock_context.state.messages[-1] == Message(creator=Agents.PLANNER, content=expected_plan.model_dump_json())
