import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from models.prompts import PromptRegistryConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class PromptRegistrySettings(BaseModel):
    """Prompt Registry Settings."""

    planner: PromptRegistryConfig = PromptRegistryConfig(name="")
    executor: PromptRegistryConfig = PromptRegistryConfig(name="")
    web_researcher: PromptRegistryConfig = PromptRegistryConfig(name="")
    synthesizer: PromptRegistryConfig = PromptRegistryConfig(name="")
    chart_summarizer: PromptRegistryConfig = PromptRegistryConfig(name="")
    visualizer: PromptRegistryConfig = PromptRegistryConfig(name="")


class OpenAISettings(BaseModel):
    """OpenAI Settings."""

    key: str = "test"
    planner_llm: str = "o3"
    executor_llm: str = "o3"
    web_search_llm: str = "o3-mini"
    synthesizer_llm: str = "o3"
    chart_summarizer_llm: str = "o3"
    visualizer_llm: str = "o3"


class TavilySettings(BaseModel):
    """Tavily Settings."""

    key: str = "test"
    max_results: int = 3


class LangfuseSettings(BaseModel):
    """Langfuse Settings."""

    secret_key: str = ""
    public_key: str = ""
    base_url: str = "https://cloud.langfuse.com"


class AgentSettings(BaseSettings):
    """Main settings class."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "settings.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    prompt_registry: PromptRegistrySettings = PromptRegistrySettings()
    openai: OpenAISettings = OpenAISettings()
    tavily: TavilySettings = TavilySettings()
    langfuse: LangfuseSettings = LangfuseSettings()

    max_replans: int = 0
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    def model_post_init(self, __context: object) -> None:  # noqa: D102, PYI063
        os.environ["LANGFUSE_SECRET_KEY"] = self.langfuse.secret_key
        os.environ["LANGFUSE_PUBLIC_KEY"] = self.langfuse.public_key
        os.environ["LANGFUSE_BASE_URL"] = self.langfuse.base_url
        os.environ["OPENAI_API_KEY"] = self.openai.key
        os.environ["TAVILY_API_KEY"] = self.tavily.key


settings = AgentSettings()
