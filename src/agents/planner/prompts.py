from core.settings import settings
from models.agents import LIST_OF_ENABLED_AGENTS_FOR_PLANNER, Agents, get_agent_descriptions
from models.prompts import PromptRole
from models.state import Plan, State
from prompt_management.registry import get_compiled_prompt_from_registry


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


def planner_system_prompt(enabled_agents: list[Agents]) -> str | None:
    """Build the system prompt for the Panner to return a high-level plan."""
    agent_list = format_agent_list_for_planning(enabled_agents)
    agent_guidelines = format_agent_guidelines_for_planning(enabled_agents)
    prompt_params = {"agent_list": agent_list, "agent_guidelines": agent_guidelines}

    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.planner, prompt_params=prompt_params, role=PromptRole.SYSTEM
    )


def planner_instruction_prompt(enabled_agents: list[Agents]) -> str | None:
    """Build instruction prompt for the Planner to return a high-level plan."""
    agent_list = format_agent_list_for_planning(enabled_agents)
    agent_guidelines = format_agent_guidelines_for_planning(enabled_agents)
    prompt_params = {"agent_list": agent_list, "agent_guidelines": agent_guidelines}

    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.planner, prompt_params=prompt_params, role=PromptRole.INSTRUCTIONS
    )


def planner_user_prompt(state: State) -> str | None:
    """Build the user prompt for the Planner to return a high-level plan."""
    prompt_params = {"user_query": state.user_query}

    if state.replan_flag:
        replan_reason = state.last_reason or ""
        current_plan = state.plan or Plan(steps=[])
        current_plan_str = current_plan.model_dump_json()
        prompt_params.update({"replan_reason": replan_reason, "current_plan": current_plan_str})

    role = PromptRole.USER_REPLAN if state.replan_flag else PromptRole.USER_PLAN

    return get_compiled_prompt_from_registry(
        prompt_config=settings.prompt_registry.planner, prompt_params=prompt_params, role=role
    )
