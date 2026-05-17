import asyncio
from argparse import ArgumentParser, Namespace
from uuid import uuid4

from langfuse import get_client, propagate_attributes

from agents import PlannerNode
from core.logger import logger
from graph import graph
from models.agents import Agents
from models.state import Message, State

enabled_agents: list[Agents] = [
    Agents.WEB_RESEARCHER,
    Agents.VISUALIZER,
    Agents.CHART_SUMMARIZER,
    Agents.SYNTHESIZER,
]


langfuse_client = get_client()


async def main(query: str) -> str:
    """Execute agent to answer the users question."""
    logger.info("Create initial state based on user's query and list of enabled agents...")
    state = State(messages=[Message(content=query)], user_query=query, enabled_agents=enabled_agents)

    session_id = f"cli-{uuid4()}"

    logger.info("Invoke multi-agent with Langfuse tracing...")
    # Wrap the full multi-agent run in a Langfuse observation and attach
    # high-level context so all emitted spans are grouped and query-specific.
    with langfuse_client.start_as_current_observation(as_type="span", name="data-agent-query"):
        with propagate_attributes(
            session_id=session_id,
            tags=["data-agent", "cli"],
            metadata={"query": query},
        ):
            await graph.run(start_node=PlannerNode(), state=state)

    logger.info("Finish asking agent...")
    return state.messages[-1].content


def parse_args() -> Namespace:
    """Parse CLI input."""
    parser = ArgumentParser()
    parser.add_argument("--query", type=str, help="User query to pass to the agent.")
    return parser.parse_args()


if __name__ == "__main__":
    query = parse_args().query
    logger.info("User's query: %s", query)

    resp = asyncio.run(main(query=query))
    logger.info("Agent's answer:\n%s", resp)

    # Ensure all observations are sent before the process exits.
    langfuse_client.flush()
