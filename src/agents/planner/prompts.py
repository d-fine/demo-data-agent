from models.agents import LIST_OF_ENABLED_AGENTS_FOR_PLANNER, Agents, get_agent_descriptions
from models.state import Plan, State


def format_agent_list_for_planning(enabled_agents: list[Agents]) -> str:
    """Format agent descriptions for the planning system prompt."""
    descriptions = get_agent_descriptions()
    enabled_agents = [_agent for _agent in enabled_agents if _agent in LIST_OF_ENABLED_AGENTS_FOR_PLANNER]
    agent_capability_list = []

    for agent_key, details in descriptions.items():
        if agent_key not in enabled_agents:
            continue
        agent_capability_list.append(f"- `{agent_key.value}` - {details.capability}")

    return "\n".join(agent_capability_list)


def format_agent_guidelines_for_planning(enabled_agents: list[Agents]) -> str:
    """Format agent usage guidelines for the planning system prompt."""
    descriptions = get_agent_descriptions()
    guidelines = []

    # Web researcher (only include guidance for enabled agents)
    if Agents.WEB_RESEARCHER in enabled_agents:
        web_desc = descriptions[Agents.WEB_RESEARCHER]
        guidelines.append(f"- Use `{Agents.WEB_RESEARCHER.value}` for {web_desc.use_when.lower()}.")

    # Chart generator specific rules
    if Agents.VISUALIZER in enabled_agents:
        chart_desc = descriptions[Agents.VISUALIZER]

        if chart_desc.position_requirement is None:
            msg = f"Position requirement in the description of agent '{Agents.VISUALIZER.value}' is missing."
            raise ValueError(msg)

        cs_hint = (
            f" A `{Agents.CHART_SUMMARIZER.value}` should be used to summarize the chart."
            if Agents.CHART_SUMMARIZER in enabled_agents
            else ""
        )
        guidelines.append(
            f"- **Include `{Agents.VISUALIZER.value}` _only_ if {chart_desc.use_when.lower()}**. "
            f"If included, `{Agents.VISUALIZER.value}` must be {chart_desc.position_requirement.lower()}. "
            "Visualizations should include all of the data from the previous steps "
            f"that is reasonable for the chart type.{cs_hint}"
        )

    # Synthesizer default
    if Agents.SYNTHESIZER in enabled_agents:
        synth_desc = descriptions[Agents.SYNTHESIZER]

        if synth_desc.position_requirement is None:
            msg = f"Position requirement in the description of agent '{Agents.SYNTHESIZER.value}' is missing."
            raise ValueError(msg)

        guidelines.append(
            f"- Otherwise use `{Agents.SYNTHESIZER.value}` as {synth_desc.position_requirement.lower()}, "
            "and be sure to include all of the data from the previous steps."
        )

    return "\n".join(guidelines)


def planner_system_prompt(enabled_agents: list[Agents]) -> str:
    """Build the system prompt for the Planner to return a high-level plan.

    This is the inline equivalent of the template previously stored in
    `prompt_management/planner/system_prompt.py`.
    """
    agent_list = format_agent_list_for_planning(enabled_agents)
    agent_guidelines = format_agent_guidelines_for_planning(enabled_agents)

    return f"""
You are the **Planner** in a multi-agent system. Break the user's request into a sequence of numbered steps
(1, 2, 3, ...). **There is no hard limit on step count** as long as the plan is concise and each step has a
clear goal.

You may decompose the user's query into sub-queries, each of which is a separate step. Break each query into the
smallest possible sub-queries so that each sub-query is answerable with a single data source.
For example, if the user's query is "What were the key action items in the last quarter, and what was a recent
news story for each of them?", you may break it into steps:

1. Fetch the key action items in the last quarter.
2. Fetch a recent news story for the first action item.
3. Fetch a recent news story for the second action item.
4. Fetch a recent news story for the last action item.

Here is a list of available agents you can call upon to execute the tasks in your plan. You may call only one
agent per step.

{agent_list}

Guidelines:
{agent_guidelines}
"""


def planner_instruction_prompt(enabled_agents: list[Agents]) -> str:
    """Build instruction prompt for the Planner to return a high-level plan.

    These instructions focus on the expected Plan structure and agent usage.
    """
    agent_list = format_agent_list_for_planning(enabled_agents)
    agent_guidelines = format_agent_guidelines_for_planning(enabled_agents)

    return f"""
You create a high-level **Plan** that describes how to answer the user's query.

- Use only these agents in the plan: {agent_list}
- Follow these guidelines when assigning agents to steps:
{agent_guidelines}

Return a JSON object matching the `Plan` schema with:
- "type": "initial" for a first plan or "replan" when revising an existing plan
- "steps": a list of objects with:
  - "step_id": an integer step index starting at 1
  - "instruction": an object with:
    - "agent": one of the supported agent names
    - "action": a short description of what that agent should do in the step
"""


def planner_user_prompt(state: State) -> str:
    """Build the user prompt for the Planner to return a high-level plan.

    This uses inline templates equivalent to those previously stored under
    `prompt_management/planner/plan_user_prompt.py` and
    `prompt_management/planner/replan_user_prompt.py`.
    """
    if not state.replan_flag:
        return f"""Generate a new plan from scratch.

User query: '{state.user_query}'
"""

    replan_reason = state.last_reason or ""
    current_plan = state.plan or Plan(steps=[])
    current_plan_str = current_plan.model_dump_json()

    return f"""
The current plan needs revision because: {replan_reason}

Current plan:
{current_plan_str}

User query: '{state.user_query}'

When replanning:
- Focus on **UNBLOCKING** the workflow rather than perfecting it.
- Only modify steps that are truly preventing progress.
- Prefer simpler, more achievable alternatives over complex rewrites.
"""
