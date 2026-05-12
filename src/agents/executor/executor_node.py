from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic_graph import BaseNode, End, GraphRunContext

from agents.executor.executor import executor
from agents.executor.prompts import executor_user_prompt
from core.errors import MissingPlanError, OutputFormatError
from core.logger import logger
from core.settings import settings
from models.agents import Agents
from models.state import DetailedAgentInstruction, Message, State

if TYPE_CHECKING:
    from agents import ChartSummarizerNode, PlannerNode, SynthesizerNode, VisualizerNode, WebResearchNode


class ExecutorNode(BaseModel, BaseNode[State, None, None]):
    """ExecutorNode built with pydantic-graph."""

    async def run(
        self, ctx: GraphRunContext[State]
    ) -> "PlannerNode | SynthesizerNode | WebResearchNode | VisualizerNode | ChartSummarizerNode | End":
        """Run the executor node.

        Creates the user prompt for the Executor Agent. Requests a specific instruction from the Executor Agent.
        Decide which node to run next based on the instruction.

        Args:
            ctx (GraphRunContext[State]): Gives the State-instance as context to the node.

        Returns:
            PlannerNode | SynthesizerNode | WebResearchNode | VisualizerNode | ChartSummarizerNode | End:
            Calls the next node after running the node.

        """
        plan = ctx.state.plan
        if plan is None:
            raise MissingPlanError

        if self.__is_end_of_plan(state=ctx.state):
            logger.info(
                "Reached end of plan at step %s. Stopping multi-agent execution.",
                ctx.state.current_step,
            )
            return End(None)

        if ctx.state.replan_flag:
            planned_agent = plan.get_step(step_id=ctx.state.current_step).instruction.agent
            logger.info("Initialize execution of planned agent '%s' due to replanning...", planned_agent)
            output = DetailedAgentInstruction(
                replan=False,
                goto=planned_agent,
                reason="Following the suggested plan after replanning.",
                query=plan.get_step(step_id=ctx.state.current_step).instruction.action,
            )
            self.__update_state(state=ctx.state, output=output)
            return self.__select_next_node(next_agent=planned_agent)

        logger.info("Invoke LLM in executor node to analyse and refine the %s. step...", ctx.state.current_step)
        user_prompt = executor_user_prompt(ctx.state)
        output = await self.__call_agent(prompt=user_prompt, ctx=ctx)

        logger.debug("Update multi-agent state...")
        self.__update_state(state=ctx.state, output=output)

        next_agent = output.goto
        return self.__select_next_node(next_agent=next_agent)

    def __update_state(self, state: State, output: DetailedAgentInstruction) -> None:
        state.messages.append(Message(creator=Agents.EXECUTOR, content=output.model_dump_json()))
        state.last_reason = output.reason
        state.agent_query = output.query

        if output.replan:
            self.__update_state_before_replanning(state=state)
            return

        self.__update_state_next_node(state=state, next_agent=output.goto)

    def __update_state_next_node(self, state: State, next_agent: Agents) -> None:
        plan = state.plan
        if plan is None:
            raise MissingPlanError
        step = state.current_step
        planned_agent = plan.get_step(step_id=state.current_step).instruction.agent

        state.replan_flag = False
        state.current_step = step + 1 if next_agent == planned_agent else step  # advance only if following the plan

    def __update_state_before_replanning(self, state: State) -> None:
        step = state.current_step
        replans = state.replan_attempts
        step_replans = replans.get(step, 0)

        if step_replans < settings.max_replans:
            state.replan_flag = True
            replans[step] = step_replans + 1
            state.replan_attempts = replans
            return

        logger.warning("Maximum number of replaned attempts failed. Moving to the next agent.")
        state.current_step = step + 1

    @staticmethod
    async def __call_agent(prompt: str, ctx: GraphRunContext[State]) -> DetailedAgentInstruction:
        response = await executor.run(user_prompt=prompt, deps=ctx.state)
        logger.debug("Executor output: %s", response.output)

        if not isinstance(response.output, DetailedAgentInstruction):
            raise OutputFormatError(value=response.output)

        return response.output

    @staticmethod
    def __select_next_node(
        next_agent: Agents,
    ) -> "PlannerNode | WebResearchNode | SynthesizerNode | VisualizerNode | ChartSummarizerNode | End":
        """Select which node to run next."""
        from agents import (  # noqa: PLC0415
            ChartSummarizerNode,
            PlannerNode,
            SynthesizerNode,
            VisualizerNode,
            WebResearchNode,
        )

        match next_agent:
            case Agents.PLANNER:
                return PlannerNode()
            case Agents.WEB_RESEARCHER:
                return WebResearchNode()
            case Agents.VISUALIZER:
                return VisualizerNode()
            case Agents.CHART_SUMMARIZER:
                return ChartSummarizerNode()
            case Agents.SYNTHESIZER:
                return SynthesizerNode()
            case _:
                logger.warning("Unsupported agent '%s'. Stop multi-agent.", next_agent)
                return End(None)

    @staticmethod
    def __is_end_of_plan(state: State) -> bool:
        """Return True if the current step index is below or equal the last step of the plan."""
        plan = state.plan
        if plan is None:
            raise MissingPlanError

        return state.current_step > len(plan.steps)
