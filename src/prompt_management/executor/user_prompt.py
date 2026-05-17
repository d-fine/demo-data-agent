prompt = """
Create a specific agent instruction relying on the following context:
- User query ...............: {user_query}
- Current step index .......: {current_step}
- Current plan step ........: {plan}
- Just-replanned flag ......: {replan_flag}
- Previous messages ........: {messages_tail}

**PRIORITIZE FORWARD PROGRESS:** Only replan if the current step is completly blocked.
1. If any reasonable data was obtained that addresses the step's core goal, set `"replan": false` and proceed.
2. Set `"replan": true` **only if** all the conditions are met:
    - The step has produced zero useful information.
    - The missing information cannot be approximated or obtained by remaining steps.
    - `{attempts} < {max_replans}`.
3. When `{attempts} == {max_replans}`, always move forward by setting `"replan": false`.

### Decide `"goto"`
- If `"replan": true`   →    `"goto": "{planner_agent}"`.
- If current step has made reasonable progress  →    `"goto": "{next_step_agent}"`.
- Otherwise execute the current step's assigned agent  →    `"goto": "{current_step_agent}"`.

### Build `"query"`
Write a clear, standalone instruction for the chosen agent. If the chosen agent is
`{web_researcher_agent}`, the query should be a standalone
question, written in plain english, and answerable by the agent.

Ensure that the query uses consistent language as the user's query.
"""
