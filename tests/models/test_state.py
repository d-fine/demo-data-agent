# ruff: noqa: S101
from copy import deepcopy

import pytest

from models.agents import Agents
from models.state import Instruction, Message, Plan, State, Step


@pytest.fixture
def mock_plan() -> Plan:
    """Initialize plan for testing purposes."""
    return Plan(
        steps=[
            Step(step_id=1, instruction=Instruction(agent=Agents.WEB_RESEARCHER, action="")),
            Step(step_id=2, instruction=Instruction(agent=Agents.SYNTHESIZER, action="")),
        ],
    )


@pytest.fixture
def mock_state() -> State:
    """Initialize state for testing purposes."""
    return State(
        messages=[Message(content="")],
        enabled_agents=[Agents.WEB_RESEARCHER, Agents.SYNTHESIZER],
        user_query="",
    )


def test_state_get_step(mock_plan: Plan, mock_state: State) -> None:
    """Verify if get_step-method of Plan is working as expected."""
    state = deepcopy(mock_state)
    state.plan = mock_plan

    step = state.plan.get_step(step_id=1)
    assert step is not None
    assert step.step_id == 1
    assert step.instruction.agent == Agents.WEB_RESEARCHER


def test_state_get_step_for_missing_step(mock_plan: Plan, mock_state: State) -> None:
    """Verify if get_step-method of Plan is working as expected if step_id is not contained in Plan."""
    state = deepcopy(mock_state)
    state.plan = mock_plan

    with pytest.raises(ValueError, match="Plan does not contain step with id 99"):
        _ = state.plan.get_step(step_id=99)
