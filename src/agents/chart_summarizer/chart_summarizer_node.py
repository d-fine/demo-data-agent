from pydantic import BaseModel
from pydantic_graph import BaseNode, End, GraphRunContext

from agents.chart_summarizer.chart_summarizer import chart_summarizer
from agents.chart_summarizer.prompts import chart_summarizer_user_prompt
from core.errors import OutputFormatError
from core.logger import logger
from models.agents import Agents
from models.state import Message, State


class ChartSummarizerNode(BaseModel, BaseNode[State, None, None]):
    """VisualizerNode node build with pydantic-graph."""

    async def run(self, ctx: GraphRunContext[State]) -> End:
        """Run the chart summarizer node.

        Summarizes the multi-agent response.

        Args:
            ctx (GraphRunContext[State]): Gives the State-instance as context to the node.

        Returns:
            End: Calls the End node after running the node.

        """
        logger.info("Invoke LLM in chart summarizer node to create a graph answering the user's query...")
        user_prompt = chart_summarizer_user_prompt(ctx.state)
        response = await chart_summarizer.run(user_prompt=user_prompt)
        output = response.output
        logger.debug("Chart summarizer output: %s", output)

        if not isinstance(output, Message):
            raise OutputFormatError(output)

        logger.debug("Update multi-agent state...")
        output.creator = Agents.CHART_SUMMARIZER
        ctx.state.messages.append(output)

        return End(None)
