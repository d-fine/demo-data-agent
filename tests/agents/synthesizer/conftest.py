import pytest
from pydantic_graph import GraphRunContext

from models.agents import Agents
from models.state import Instruction, Message, Plan, State, Step


@pytest.fixture
def mock_state() -> State:
    """Mock state for testing purposes."""
    return State(
        messages=[
            Message(creator=Agents.PLANNER, content="Test plan."),
            Message(creator=Agents.EXECUTOR, content="Test executor msg."),
            Message(creator=Agents.WEB_RESEARCHER, content="Web research result 1."),
            Message(creator=Agents.WEB_RESEARCHER, content="Web research result 2."),
        ],
        user_query="Test user query.",
        enabled_agents=[Agents.WEB_RESEARCHER, Agents.SYNTHESIZER],
        current_step=2,
        plan=Plan(
            steps=[
                Step(step_id=1, instruction=Instruction(agent=Agents.WEB_RESEARCHER, action="First instruction.")),
                Step(step_id=2, instruction=Instruction(agent=Agents.SYNTHESIZER, action="Second instruction.")),
            ]
        ),
        agent_query="Test agent query.",
        last_reason=None,
        replan_flag=False,
        replan_attempts={1: 0},
    )


@pytest.fixture
def mock_context(mock_state: State) -> GraphRunContext[State, None]:
    """Mock run context for testing purposes."""
    return GraphRunContext(state=mock_state, deps=None)
