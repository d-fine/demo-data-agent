import pytest
from pydantic_graph import GraphRunContext

from models.agents import Agents
from models.state import Message, State


@pytest.fixture
def mock_state() -> State:
    """Mock state for testing purposes."""
    msg = Message(creator=None, content="Test message.")
    return State(
        messages=[msg],
        user_query="Test user query.",
        enabled_agents=[Agents.WEB_RESEARCHER, Agents.SYNTHESIZER],
        current_step=1,
        plan=None,
        agent_query=None,
        last_reason=None,
        replan_flag=False,
        replan_attempts={1: 0},
    )


@pytest.fixture
def mock_context(mock_state: State) -> GraphRunContext[State, None]:
    """Mock run context for testing purposes."""
    return GraphRunContext(state=mock_state, deps=None)
