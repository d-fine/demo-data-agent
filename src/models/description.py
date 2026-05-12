from pydantic import BaseModel


class AgentDescription(BaseModel):
    """Description class for agents."""

    name: str
    capability: str
    use_when: str
    limitations: str
    output_format: str
    position_requirement: str | None = None
