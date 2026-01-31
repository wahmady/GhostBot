"""
GhostBot Core Module

This module contains the core components for the AI Mobile QA & UX Auditor Agent.
"""

from .driver import MobileDriver
from .brain import AIBrain, OpenAIBrain, AnthropicBrain, BaseBrain, create_brain
from .optimizer import encode_image
from .logger import TestReporter
from .prompts import SYSTEM_PROMPT

__all__ = [
    "MobileDriver",
    "AIBrain",
    "OpenAIBrain",
    "AnthropicBrain",
    "BaseBrain",
    "create_brain",
    "encode_image",
    "TestReporter",
    "SYSTEM_PROMPT",
]
