from agents.common.prompts import common_system_prompt


def web_researcher_system_prompt() -> str:
    """Build the system prompt for the Web-Researcher to return a web-research result."""
    specific_sytem_prompt = """
You are the **Web-Researcher**. You can ONLY perform research by using the provided search tool (tavily_tool).
When you have found the necessary information, end your output. Do NOT attempt to take further actions.
"""
    return common_system_prompt + f"\n{specific_sytem_prompt}"
