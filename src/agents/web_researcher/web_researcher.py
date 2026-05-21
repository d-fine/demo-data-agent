from pydantic_ai import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

from agents.web_researcher.prompts import web_researcher_system_prompt
from core.settings import settings
from models.state import Message

web_researcher = Agent(
    model=f"openai:{settings.openai.web_search_llm}",
    tools=[tavily_search_tool(api_key=settings.tavily.key)],
    output_type=Message,
    instrument=True,
)


@web_researcher.system_prompt
async def add_system_prompt() -> str | None:
    """Create and add web researcher system prompt to Web Researcher agent."""
    return web_researcher_system_prompt()
