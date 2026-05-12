from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class PromptRole(StrEnum):
    """Supported prompt roles."""

    SYSTEM = "system"
    INSTRUCTIONS = "instructions"
    USER_REPLAN = "user_replan"
    USER_PLAN = "user_plan"


class PromptRegistryConfig(BaseModel):
    """Prompt registry config to select prompt from Prompt Registry."""

    name: str
    type: Literal["chat", "text"] = "text"
    label: str | None = None
    version: int | None = None
