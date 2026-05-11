from __future__ import annotations

from pydantic import BaseModel
from pydantic_graph import BaseNode, GraphRunContext

from agents.executor.executor_node import ExecutorNode
from agents.visualizer.prompts import visualizer_user_prompt
from agents.visualizer.visualizer import visualizer
from core.errors import OutputFormatError
from core.logger import logger
from models.agents import Agents
from models.state import Message, State


class VisualizerNode(BaseModel, BaseNode[State, None, None]):
    """VisualizerNode node build with pydantic-graph."""

    async def run(self, ctx: GraphRunContext[State]) -> ExecutorNode:
        """Run the visualizer node.

        Executes the visualization by creating `matplotlib`-charts using the `run_matplotlib`-tool.

        Args:
            ctx (GraphRunContext[State]): Gives the State-instance as context to the node.

        Returns:
            End: Calls the End node after running the node.

        """
        logger.info("Invoke LLM in visualizer node to create a graph answering the user's query...")
        user_prompt = visualizer_user_prompt(ctx.state)
        response = await visualizer.run(user_prompt=user_prompt)
        output = response.output
        logger.debug("Visualizer output: %s", output)

        if not isinstance(output, Message):
            raise OutputFormatError(output)

        logger.debug("Update multi-agent state...")
        output.creator = Agents.VISUALIZER
        ctx.state.messages.append(output)

        return ExecutorNode()
