from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic_graph import BaseNode, GraphRunContext

from agents.web_researcher.web_researcher import web_researcher
from core.errors import OutputFormatError
from core.logger import logger
from models.agents import Agents
from models.state import Message, State

if TYPE_CHECKING:
    from agents.executor.executor_node import ExecutorNode


class WebResearchNode(BaseModel, BaseNode[State, None, None]):
    """WebResearchNode node build with pydantic-graph."""

    async def run(self, ctx: GraphRunContext[State]) -> "ExecutorNode":
        """Run the web-research node.

        Executes web research using tavily tool.

        Args:
            ctx (GraphRunContext[State]): Gives the State-instance as context to the node.

        Returns:
            ExecutorNode: Calls the executor node after running the node.

        """
        from agents.executor.executor_node import ExecutorNode  # noqa: PLC0415

        logger.info("Invoke LLM in web researcher node to execute a web research...")
        user_prompt = ctx.state.agent_query
        response = await web_researcher.run(user_prompt=user_prompt)
        output = response.output
        logger.debug("Web research output: %s", output)

        if not isinstance(output, Message):
            raise OutputFormatError(output)

        logger.debug("Update multi-agent state...")
        output.creator = Agents.WEB_RESEARCHER
        ctx.state.messages.append(output)

        return ExecutorNode()
