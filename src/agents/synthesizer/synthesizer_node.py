from pydantic import BaseModel
from pydantic_graph import BaseNode, End, GraphRunContext

from agents.synthesizer.prompts import synthesizer_user_prompt
from agents.synthesizer.synthesizer import synthesizer
from core.errors import OutputFormatError
from core.logger import logger
from models.agents import Agents
from models.state import Message, State


class SynthesizerNode(BaseModel, BaseNode[State, None, None]):
    """SynthesizerNode node build with pydantic-graph."""

    async def run(self, ctx: GraphRunContext[State]) -> End:
        """Run the synthesizer node.

        Summarizes the multi-agent response.

        Args:
            ctx (GraphRunContext[State]): Gives the State-instance as context to the node.

        Returns:
            End: Calls the End node after running the node.

        """
        logger.info("Invoke LLM in synthesizer node to summarize and answer the user's query...")
        user_prompt = synthesizer_user_prompt(ctx.state)
        response = await synthesizer.run(user_prompt=user_prompt)
        output = response.output
        logger.debug("Synthesizer output: %s", output)

        if not isinstance(output, Message):
            raise OutputFormatError(output)

        logger.debug("Update multi-agent state...")
        output.creator = Agents.SYNTHESIZER
        ctx.state.messages.append(output)

        return End(None)
