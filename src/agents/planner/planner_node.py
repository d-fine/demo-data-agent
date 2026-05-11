from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic_graph import BaseNode, GraphRunContext

from agents.planner.planner import planner
from agents.planner.prompts import planner_user_prompt
from core.errors import OutputFormatError
from core.logger import logger
from models.agents import Agents
from models.state import Message, Plan, PlanType, State

if TYPE_CHECKING:
    from agents.executor.executor_node import ExecutorNode


class PlannerNode(BaseModel, BaseNode[State, None, None]):
    """PlannerNode built with pydantic-graph."""

    async def run(self, ctx: GraphRunContext[State]) -> "ExecutorNode":
        """Run the planner node.

        Creates the user prompt for the Planner Agent. Requests a plan from the Planner Agents.
        Updates the state based on the returned plan.

        Args:
            ctx (GraphRunContext[State]): Gives the State-instance as context to the node.

        Returns:
            ExecutorNode: Calls the executor node after running the node.

        """
        from agents.executor.executor_node import ExecutorNode  # noqa: PLC0415

        logger.info("Invoke LLM in planner node to generate a plan...")
        user_prompt = planner_user_prompt(ctx.state)
        output = await self.__call_agent(prompt=user_prompt, state=ctx.state)

        self.__correct_plan_type_to_align_with_state(state=ctx.state, output=output)
        self.__reset_step_to_align_with_replanning(state=ctx.state)
        logger.debug("Update multi-agent state...")
        self.__update_state(state=ctx.state, output=output)

        return ExecutorNode()

    @staticmethod
    async def __call_agent(prompt: str | None, state: State) -> Plan:
        response = await planner.run(user_prompt=prompt, deps=state)
        logger.debug("Planner output: %s", response.output)

        if not isinstance(response.output, Plan):
            raise OutputFormatError(value=response.output)

        return response.output

    @staticmethod
    def __correct_plan_type_to_align_with_state(state: State, output: Plan) -> None:
        if state.replan_flag and output.type == PlanType.INITIAL:
            logger.warning(
                "Planner has replanned, but plan type '%s' does not indicate this. Adjusting plan type.", output.type
            )
            output.type = PlanType.REPLAN

        if not state.replan_flag and output.type == PlanType.REPLAN:
            logger.warning(
                "Planner created initial plan, but plan typ e'%s' does not indicate this. Adjusting plan type.",
                output.type,
            )
            output.type = PlanType.INITIAL

    @staticmethod
    def __update_state(state: State, output: Plan) -> None:
        state.messages.append(Message(creator=Agents.PLANNER, content=output.model_dump_json()))
        state.plan = output

    @staticmethod
    def __reset_step_to_align_with_replanning(state: State) -> None:
        if state.replan_flag:
            logger.warning(
                "Planner has replanned, but current step '%s' does not indicate this. Adjusting current step.",
                state.current_step,
            )
            state.current_step = 1
