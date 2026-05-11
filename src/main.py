import asyncio
from argparse import ArgumentParser, Namespace

from agents import PlannerNode
from core.logger import logger
from graph import graph
from models.agents import Agents
from models.state import Message, State

enabled_agents: list[Agents] = [Agents.WEB_RESEARCHER, Agents.VISUALIZER, Agents.CHART_SUMMARIZER, Agents.SYNTHESIZER]


async def main(query: str) -> str:
    """Execute agent to answer the users question."""
    logger.info("Create initial state based on user's query and list of enabled agents...")
    state = State(messages=[Message(content=query)], user_query=query, enabled_agents=enabled_agents)

    logger.info("Invoke multi-agent...")
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
