"""Shared helpers for Langfuse prompt registry integration.

This module centralizes the logic for retrieving and compiling prompts from the
Langfuse Prompt Management system so that all agents can reuse the same
implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import langfuse

from core.logger import logger

if TYPE_CHECKING:
    from models.prompts import PromptRegistryConfig, PromptRole


langfuse_client = langfuse.get_client()


def _get_prompt_from_chat_prompt(chat_prompt: list[dict[str, str]], role: PromptRole) -> str | None:
    """Get specific role prompt from chat prompt."""
    try:
        prompt = next((p["content"] for p in chat_prompt if p.get("role") == role), None)

    except AttributeError as err:
        msg = "Received prompt from the Prompt registry is not a chat prompt."
        raise ValueError(msg) from err

    if prompt is None:
        logger.info("No prompt is available for role '%s'.", role)

    return prompt


def get_compiled_prompt_from_registry(
    prompt_config: PromptRegistryConfig,
    prompt_params: dict[str, str] | None,
    role: PromptRole | None,
) -> str | None:
    """Get compiled prompt from Prompt Registry.

    Params:
        prompt_config: Metadata used to retrieve a specific prompt from the
            Prompt Registry.
        prompt_params: Parameters used to format the registered prompt in case
            it contains placeholders.
        role: Required for prompts of type "chat" in order to select the
            desired role prompt.

    Returns:
        The compiled prompt string, or ``None`` if no suitable prompt is
        available.

    """
    raw_prompt_obj = langfuse_client.get_prompt(**prompt_config.model_dump())
    raw_prompt = raw_prompt_obj.prompt

    if prompt_config.type == "chat":
        if role is None:
            msg = "Missing role specification to select role prompt from chat prompt."
            raise ValueError(msg)

        raw_prompt = _get_prompt_from_chat_prompt(chat_prompt=raw_prompt, role=role)  # type: ignore[arg-type]

    if raw_prompt is None or not isinstance(raw_prompt, str):
        return None

    return raw_prompt.format(**(prompt_params or {}))
