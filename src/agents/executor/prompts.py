from core.errors import MissingPlanError
from core.settings import settings
from models.agents import (
    LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR,
    Agents,
    get_agent_descriptions,
)
from models.state import State


def format_agent_list_for_execution(enabled_agents: list[Agents]) -> str:
    """Format agent descriptions for the execution system prompt."""
    enabled_agents = [_agent for _agent in enabled_agents if _agent in LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR]
    return f"`{{{', '.join(sorted(set(enabled_agents)))}}}"


def format_agent_guidelines_for_execution(enabled_agents: list[Agents]) -> str:
    """Format agent usage guidelines for the executor prompt."""
    descriptions = get_agent_descriptions()
    enabled_agents = [_agent for _agent in enabled_agents if _agent in LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR]
    guidelines = []

    if Agents.WEB_RESEARCHER in enabled_agents:
        web_desc = descriptions[Agents.WEB_RESEARCHER]
        guidelines.append(f"- Use `{Agents.WEB_RESEARCHER.value}` when {web_desc.use_when.lower()}.")

    return "\n".join(guidelines)


def executor_system_prompt(enabled_agents: list[Agents]) -> str:
    """Build a system prompt for the Executor to return a specific agent instruction."""
    agent_list = format_agent_list_for_execution(enabled_agents)
    agent_guidelines = format_agent_guidelines_for_execution(enabled_agents)
    return f"""
You are the **Executor** in a multi-agent system with these agents:

{agent_list}.

**Tasks**
Create a specific agent instruction including the following information:
    1. Decide if the current plan need revision.                    →   `"replan_flag": true|false`
    2. Decide which agent to run next.                              →   `"goto": "<agent_name>"`
    3. Give one-sentence justification.                             →   `"reason": "<text>"`
    4. Write the exact question that the chosen agent should answer →   "query": "<text>"

**Guidelines**
{agent_guidelines}
- After **{settings.max_replans}** failed replans for the same step, move on.
- If you *just replanned* (replan_flag is true) let the assigned agent type before requesting another replan.
"""


def executor_user_prompt(state: State) -> str:
    """Build the user prompt for the Executor to return a specific agent instruction."""
    # Get the replan attempts for the current step, if available. Otherwise sets it to 0.
    attempts = (state.replan_attempts or {}).get(state.current_step, 0)
    messages_tail = state.messages[-4:]
    plan = state.plan
    if plan is None:
        raise MissingPlanError

    current_step_agent = plan.get_step(step_id=state.current_step).instruction.agent
    next_step_agent = plan.get_step(step_id=state.current_step)

    return f"""
Create a specific agent instruction relying on the following context:
- User query ...............: {state.user_query}
- Current step index .......: {state.current_step}
- Current plan step ........: {plan}
- Just-replanned flag ......: {state.replan_flag}
- Previous messages ........: {messages_tail}

**PRIORITIZE FORWARD PROGRESS:** Only replan if the current step is completly blocked.
1. If any reasonable data was obtained that addresses the step's core goal, set `"replan": false` and proceed.
2. Set `"replan": true` **only if** all the conditions are met:
    - The step has produced zero useful information.
    - The missing information cannot be approximated or obtained by remaining steps.
    - `{attempts} < {settings.max_replans}`.
3. When `{attempts} == {settings.max_replans}`, always move forward by setting `"replan": false`.

### Decide `"goto"`
- If `"replan": true`   →    `"goto": "{Agents.PLANNER}"`.
- If current step has made reasonable progress  →    `"goto": "{next_step_agent}"`.
- Otherwise execute the current step's assigned agent  →    `"goto": "{current_step_agent}"`.

### Build `"query"`
Write a clear, standalone instruction for the chosen agent. If the chosen agent is
`{Agents.WEB_RESEARCHER}`, the query should be a standalone
question, written in plain english, and answerable by the agent.

Ensure that the query uses consistent language as the user's query.
"""
