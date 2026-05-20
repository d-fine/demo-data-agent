# ruff: noqa: S101

from agents.planner.prompts import planner_instruction_prompt, planner_system_prompt, planner_user_prompt
from models.state import Plan, State


def test_planner_system_prompt_includes_core_text_and_guidelines(mock_state: State) -> None:
    """System prompt should include planner description and guidelines."""
    prompt = planner_system_prompt(enabled_agents=mock_state.enabled_agents)

    assert "You are the **Planner** in a multi-agent system." in prompt
    assert "Guidelines:" in prompt
    # Ensure at least one enabled agent appears in the rendered prompt
    for agent in mock_state.enabled_agents:
        assert agent.value in prompt


def test_planner_instruction_prompt_describes_plan_schema(mock_state: State) -> None:
    """Instruction prompt should describe the expected Plan structure."""
    prompt = planner_instruction_prompt(enabled_agents=mock_state.enabled_agents)

    assert "Return a JSON object matching the `Plan` schema" in prompt
    assert "steps" in prompt
    assert "instruction" in prompt


def test_planner_user_prompt_for_initial_plan(mock_state: State) -> None:
    """User prompt for initial planning should reference the user query only."""
    mock_state.replan_flag = False
    prompt = planner_user_prompt(state=mock_state)

    assert "Generate a new plan from scratch." in prompt
    assert mock_state.user_query in prompt
    assert "Current plan" not in prompt


def test_planner_user_prompt_for_replan_includes_reason_and_plan() -> None:
    """User prompt for replanning should include reason and serialized plan."""
    state = State(
        messages=[],
        user_query="Original question",
        enabled_agents=[],
        plan=Plan(steps=[]),
        current_step=1,
        agent_query=None,
        last_reason="Previous plan failed to fetch data",
        replan_flag=True,
        replan_attempts={1: 0},
    )

    prompt = planner_user_prompt(state=state)

    assert "The current plan needs revision because:" in prompt
    assert state.last_reason in prompt
    assert "Current plan:" in prompt
    assert "When replanning:" in prompt
