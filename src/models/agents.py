from enum import StrEnum

from models.description import AgentDescription


class Agents(StrEnum):
    """Enum of supported agents."""

    VISUALIZER = "visualizer"
    CHART_SUMMARIZER = "chart_summarizer"
    SYNTHESIZER = "synthesizer"
    WEB_RESEARCHER = "web_researcher"
    PLANNER = "planner"
    EXECUTOR = "executor"


def get_agent_descriptions() -> dict[Agents, AgentDescription]:
    """Return structured agent description with capabilites and guidelines.

    Edit this function to change how the planner/executer reason about agents.

    Returns:
        dict[str, dict[str, Any]]: agents' description used by the planner/executer

    """
    return {
        Agents.WEB_RESEARCHER: AgentDescription(
            name=Agents.WEB_RESEARCHER.value,
            capability="Fetch public data via Tavily web search",
            use_when="Public information, news, current events, or external facts are needed",
            limitations="Cannot access private/internal company data",
            output_format="Raw research data and findings from public sources",
        ),
        Agents.VISUALIZER: AgentDescription(
            name=Agents.VISUALIZER.value,
            capability="Build visualizations from structured data",
            use_when=(
                "User explicitly requests charts, graphs, plots, visualizations (keywords: chart, graph, plot, "
                "visualise, bar-chart, line-chart, histogram, etc.)"
            ),
            limitations="Requires structured data input from previous steps",
            output_format="Visual charts and graphs",
            position_requirement="Must be used as final step after data gathering is complete",
        ),
        Agents.CHART_SUMMARIZER: AgentDescription(
            name=Agents.CHART_SUMMARIZER.value,
            capability="Summarize and explain chart visualizations",
            use_when="After visualizer has created a visualization",
            limitations="Requires a chart as input",
            output_format="Written summary and analysis of chart content",
            position_requirement="Should be used as final step when chart is needed",
        ),
        Agents.SYNTHESIZER: AgentDescription(
            name=Agents.SYNTHESIZER.value,
            capability="Write comprehensive prose summaries of findings",
            use_when="Final step when no visualization is requested - combines all previous research",
            limitations="Requires research data from previous steps",
            output_format="Coherent written summary incorporating all findings",
            position_requirement="Should be used as final step when no chart is needed",
        ),
    }


LIST_OF_SUPPORTED_AGENTS: list[Agents] = list(get_agent_descriptions().keys())
LIST_OF_ENABLED_AGENTS_FOR_PLANNER: list[Agents] = [
    Agents.WEB_RESEARCHER,
    Agents.VISUALIZER,
    Agents.CHART_SUMMARIZER,
    Agents.SYNTHESIZER,
]
LIST_OF_ENABLED_AGENTS_FOR_EXECUTOR: list[Agents] = [
    Agents.WEB_RESEARCHER,
    Agents.VISUALIZER,
    Agents.CHART_SUMMARIZER,
    Agents.SYNTHESIZER,
    Agents.PLANNER,
]
