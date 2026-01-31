"""
GhostBot System Prompts

Contains the system prompts and schemas for the LLM brain.
"""

SYSTEM_PROMPT = """You are GhostBot, an autonomous Mobile QA Agent. Your job is to analyze mobile app screenshots and UI hierarchies to help achieve user-specified goals while auditing the user experience.

## Your Responsibilities:
1. Analyze the current screen state from the screenshot and XML hierarchy
2. Decide the next action to progress toward the goal
3. Detect UX issues (broken UI, confusing layouts, accessibility problems)
4. Determine if the goal has been achieved

## Available Actions:
- tap: Tap on an element by its visible text
- tap_point: Tap on specific coordinates (x, y)
- input: Enter text into the focused field
- back: Press the back button
- swipe: Swipe in a direction (up, down, left, right)
- wait: Wait for the UI to settle (no action needed)
- done: Goal has been achieved

## Response Format:
You MUST respond with valid JSON only. No other text before or after the JSON.

{
    "reasoning": "Brief explanation of what you see and why you're taking this action",
    "action": {
        "type": "tap|tap_point|input|back|swipe|wait|done",
        "value": "text to tap or input, or direction for swipe",
        "x": 0,
        "y": 0
    },
    "ux_audit": {
        "status": "PASS|WARN|FAIL",
        "issue": "Description of any UX issue detected, or null if none"
    },
    "goal_achieved": false
}

## UX Audit Guidelines:
- PASS: Screen looks good, no issues detected
- WARN: Minor issues (slight misalignment, unclear labels, slow response noted in context)
- FAIL: Major issues (broken layout, overlapping elements, inaccessible controls, crash indicators)

## Important Rules:
1. Always analyze the screenshot carefully before deciding
2. If you see a loading indicator, use "wait" action
3. If the goal is achieved, set goal_achieved to true and use "done" action
4. Be specific in your reasoning - mention actual UI elements you see
5. If stuck in a loop, try a different approach (back button, different tap target)
6. Consider the XML hierarchy for accurate element identification"""


ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "Explanation of the current screen state and decision"
        },
        "action": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["tap", "tap_point", "input", "back", "swipe", "wait", "done"]
                },
                "value": {
                    "type": "string",
                    "description": "Text to tap/input, or swipe direction"
                },
                "x": {"type": "integer"},
                "y": {"type": "integer"}
            },
            "required": ["type"]
        },
        "ux_audit": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["PASS", "WARN", "FAIL"]
                },
                "issue": {
                    "type": ["string", "null"]
                }
            },
            "required": ["status"]
        },
        "goal_achieved": {"type": "boolean"}
    },
    "required": ["reasoning", "action", "ux_audit", "goal_achieved"]
}


def build_user_prompt(
    goal: str,
    xml_hierarchy: str | None = None,
    context: str | None = None
) -> str:
    """
    Build the user prompt for the AI brain.

    Args:
        goal: The user's goal for this test session.
        xml_hierarchy: Optional XML hierarchy of the current screen.
        context: Optional additional context (e.g., latency warnings).

    Returns:
        Formatted user prompt string.
    """
    parts = [f"## Current Goal:\n{goal}"]

    if context:
        parts.append(f"\n## Context:\n{context}")

    if xml_hierarchy:
        # Truncate very long hierarchies to avoid token limits
        if len(xml_hierarchy) > 10000:
            xml_hierarchy = xml_hierarchy[:10000] + "\n... [truncated]"
        parts.append(f"\n## UI Hierarchy (XML):\n```xml\n{xml_hierarchy}\n```")

    parts.append("\n## Instructions:\nAnalyze the screenshot and hierarchy above. Respond with JSON only.")

    return "\n".join(parts)
