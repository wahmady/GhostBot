"""
GhostBot AI Brain

Multi-provider AI integration layer for visual analysis and decision making.
Supports both OpenAI (GPT-4o) and Anthropic (Claude) models.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

from rich.console import Console
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .prompts import SYSTEM_PROMPT, build_user_prompt

console = Console()


class BaseBrain(ABC):
    """Abstract base class for AI brain implementations."""

    def __init__(self) -> None:
        self._last_response: Optional[dict[str, Any]] = None
        self._last_raw_response: Optional[str] = None

    @property
    def last_response(self) -> Optional[dict[str, Any]]:
        """Return the last parsed response from the AI."""
        return self._last_response

    def get_last_raw_response(self) -> Optional[str]:
        """Return the last raw response string from the AI."""
        return self._last_raw_response

    @abstractmethod
    def get_next_action(
        self,
        screenshot_b64: str,
        goal: str,
        xml_hierarchy: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """Analyze the current screen and decide on the next action."""
        pass

    def _parse_response(self, raw_content: str) -> dict[str, Any]:
        """
        Parse and validate the AI response.

        Args:
            raw_content: Raw response string from the AI.

        Returns:
            Parsed dictionary with required fields.

        Raises:
            ValueError: If response is invalid or missing required fields.
        """
        self._last_raw_response = raw_content

        if not raw_content:
            raise ValueError("Empty response from AI")

        # Try to extract JSON from the response (handle markdown code blocks)
        content = raw_content.strip()
        if content.startswith("```"):
            # Extract content between code blocks
            lines = content.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    json_lines.append(line)
            content = "\n".join(json_lines)

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse AI response as JSON:[/red] {e}")
            console.print(f"[dim]Raw response: {raw_content}[/dim]")
            raise ValueError(f"Invalid JSON response: {e}")

        self._last_response = parsed

        # Validate required fields
        required_fields = ["reasoning", "action", "ux_audit", "goal_achieved"]
        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing required field: {field}")

        return parsed


class OpenAIBrain(BaseBrain):
    """
    AI Brain implementation using OpenAI's GPT-4o vision model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
    ) -> None:
        """
        Initialize the OpenAI Brain.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            model: Model to use. Default is gpt-4o.
            base_url: Optional custom base URL for the API.
        """
        super().__init__()
        from openai import OpenAI

        self.model = os.getenv("OPENAI_MODEL", model)
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL"),
        )
        self.provider = "openai"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    def get_next_action(
        self,
        screenshot_b64: str,
        goal: str,
        xml_hierarchy: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Analyze the current screen and decide on the next action.

        Args:
            screenshot_b64: Base64-encoded screenshot image.
            goal: The goal to achieve.
            xml_hierarchy: Optional XML hierarchy of the UI.
            context: Optional additional context (e.g., latency warning).

        Returns:
            Dictionary with keys: reasoning, action, ux_audit, goal_achieved.
        """
        user_prompt = build_user_prompt(goal, xml_hierarchy, context)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{screenshot_b64}",
                            "detail": "high",
                        },
                    },
                    {"type": "text", "text": user_prompt},
                ],
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1024,
            temperature=0.1,
        )

        raw_content = response.choices[0].message.content
        return self._parse_response(raw_content)


class AnthropicBrain(BaseBrain):
    """
    AI Brain implementation using Anthropic's Claude vision models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        """
        Initialize the Anthropic Brain.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
            model: Model to use. Default is claude-sonnet-4-20250514.
        """
        super().__init__()
        from anthropic import Anthropic

        self.model = os.getenv("ANTHROPIC_MODEL", model)
        self.client = Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
        )
        self.provider = "anthropic"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True,
    )
    def get_next_action(
        self,
        screenshot_b64: str,
        goal: str,
        xml_hierarchy: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Analyze the current screen and decide on the next action.

        Args:
            screenshot_b64: Base64-encoded screenshot image.
            goal: The goal to achieve.
            xml_hierarchy: Optional XML hierarchy of the UI.
            context: Optional additional context (e.g., latency warning).

        Returns:
            Dictionary with keys: reasoning, action, ux_audit, goal_achieved.
        """
        user_prompt = build_user_prompt(goal, xml_hierarchy, context)

        # Claude uses a different message format for images
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": screenshot_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                ],
            },
        ]

        response = self.client.messages.create(
            model=self.model,
            system=SYSTEM_PROMPT,
            messages=messages,
            max_tokens=1024,
            temperature=0.1,
        )

        # Extract text from Claude's response
        raw_content = ""
        for block in response.content:
            if block.type == "text":
                raw_content = block.text
                break

        return self._parse_response(raw_content)


class AIBrain:
    """
    Factory class that creates the appropriate AI brain based on configuration.

    Supports both OpenAI (GPT-4o) and Anthropic (Claude) models.
    """

    def __new__(
        cls,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> BaseBrain:
        """
        Create an AI Brain instance based on the provider.

        Args:
            provider: AI provider ("openai" or "anthropic").
                     If None, reads from AI_PROVIDER env var (default: "openai").
            api_key: API key for the provider.
            model: Model to use. Provider-specific defaults apply.
            base_url: Optional custom base URL (OpenAI only).

        Returns:
            An instance of OpenAIBrain or AnthropicBrain.

        Raises:
            ValueError: If an unsupported provider is specified.
        """
        provider = (provider or os.getenv("AI_PROVIDER", "openai")).lower()

        if provider == "openai":
            return OpenAIBrain(
                api_key=api_key,
                model=model or "gpt-4o",
                base_url=base_url,
            )
        elif provider in ("anthropic", "claude"):
            return AnthropicBrain(
                api_key=api_key,
                model=model or "claude-sonnet-4-20250514",
            )
        else:
            raise ValueError(
                f"Unsupported AI provider: {provider}. "
                "Supported providers: 'openai', 'anthropic'"
            )


def create_brain(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> BaseBrain:
    """
    Create an AI Brain instance.

    This is an alternative factory function for creating brain instances.

    Args:
        provider: AI provider ("openai" or "anthropic").
        api_key: API key for the provider.
        model: Model to use.
        base_url: Optional custom base URL (OpenAI only).

    Returns:
        An instance of OpenAIBrain or AnthropicBrain.
    """
    return AIBrain(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
