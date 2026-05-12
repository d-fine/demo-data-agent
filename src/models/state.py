from enum import StrEnum

from pydantic import BaseModel

from models.agents import Agents


class PlanType(StrEnum):
    """Plan type enum."""

    REPLAN = "replan"
    INITIAL = "initial"


class Instruction(BaseModel):
    """Instruction model."""

    agent: Agents
    action: str


class Step(BaseModel):
    """Step model."""

    step_id: int
    instruction: Instruction


class Plan(BaseModel):
    """Plan model. Describes the structure of a plan. It is returned by the Planner and used by the Executor."""

    steps: list[Step]
    type: PlanType = PlanType.INITIAL

    def get_step(self, step_id: int) -> Step:
        """Get specific step from plan.

        Params:
            step_id (int): Number of step to be returned.

        Returns:
            Step: specific step from plan.

        Raises:
            ValueError: Plan does not contain step with id {step_id}.

        """
        step = next((_step for _step in self.steps if _step.step_id == step_id), None)
        if step is None:
            msg = f"Plan does not contain step with id {step_id}."
            raise ValueError(msg)
        return step


class DetailedAgentInstruction(BaseModel):
    """Model capturing the detailed agent instruction created by the Executor."""

    replan: bool
    goto: Agents
    reason: str
    query: str


class Message(BaseModel):
    """Model capturing the detailed agent output."""

    creator: Agents | None = None
    content: str


class State(BaseModel):
    """Data agent state model."""

    messages: list[Message]
    user_query: str  # user's original query
    enabled_agents: list[Agents]  # modularizes a multi-agent on specified list of agents
    plan: Plan | None = None
    current_step: int = 1
    agent_query: str | None = None
    last_reason: str | None = None
    replan_flag: bool = False
    replan_attempts: dict[int, int] = {1: 0}
