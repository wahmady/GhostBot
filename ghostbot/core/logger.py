"""
GhostBot Test Reporter

Handles Markdown report generation for test sessions.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class TestReporter:
    """
    TestReporter generates human-readable Markdown logs of test sessions.
    """

    def __init__(
        self,
        output_dir: str = "reports",
        session_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the TestReporter.

        Args:
            output_dir: Directory to save reports. Default is 'reports'.
            session_name: Optional custom name for this session.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if session_name:
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_name)
            self.filename = f"{timestamp}_{safe_name[:50]}.md"
        else:
            self.filename = f"{timestamp}_test_report.md"

        self.filepath = self.output_dir / self.filename
        self._step_count = 0
        self._goal: Optional[str] = None
        self._start_time = datetime.now()
        self._ux_issues: list[dict[str, Any]] = []

    def start_session(self, goal: str) -> None:
        """
        Start a new test session and write the report header.

        Args:
            goal: The goal for this test session.
        """
        self._goal = goal
        self._start_time = datetime.now()

        header = f"""# GhostBot Test Report

**Date:** {self._start_time.strftime("%Y-%m-%d %H:%M:%S")}
**Goal:** {goal}

---

"""
        self._write(header, mode="w")

    def log_step(
        self,
        action: dict[str, Any],
        reasoning: str,
        ux_audit: dict[str, Any],
        latency_ms: Optional[int] = None,
    ) -> None:
        """
        Log a single step of the test session.

        Args:
            action: The action taken (dict with 'type' and 'value').
            reasoning: The AI's reasoning for this action.
            ux_audit: UX audit result (dict with 'status' and 'issue').
            latency_ms: Optional latency measurement in milliseconds.
        """
        self._step_count += 1

        # Format action
        action_type = action.get("type", "unknown")
        action_value = action.get("value", "")
        if action_type == "tap_point":
            action_str = f"Tapped point ({action.get('x', 0)}, {action.get('y', 0)})"
        elif action_type == "tap":
            action_str = f"Tapped '{action_value}'"
        elif action_type == "input":
            action_str = f"Entered text: '{action_value}'"
        elif action_type == "swipe":
            action_str = f"Swiped {action_value}"
        elif action_type == "back":
            action_str = "Pressed Back button"
        elif action_type == "wait":
            action_str = "Waited for UI to settle"
        elif action_type == "done":
            action_str = "Goal achieved - session complete"
        else:
            action_str = f"{action_type}: {action_value}"

        # Format UX status
        ux_status = ux_audit.get("status", "PASS")
        ux_issue = ux_audit.get("issue")

        if ux_status == "PASS":
            ux_str = "PASS"
        elif ux_status == "WARN":
            ux_str = f"WARNING - {ux_issue}" if ux_issue else "WARNING"
            self._ux_issues.append({"step": self._step_count, "status": "WARN", "issue": ux_issue})
        else:
            ux_str = f"FAIL - {ux_issue}" if ux_issue else "FAIL"
            self._ux_issues.append({"step": self._step_count, "status": "FAIL", "issue": ux_issue})

        # Build step entry
        entry = f"""## Step {self._step_count}

**Action:** {action_str}
**Reasoning:** {reasoning}
**UX Status:** {ux_str}"""

        if latency_ms is not None:
            entry += f"  \n**Latency:** {latency_ms}ms"
            if latency_ms > 5000:
                entry += " (High latency detected)"

        entry += "\n\n---\n\n"

        self._write(entry)

    def end_session(self, success: bool, final_notes: Optional[str] = None) -> str:
        """
        End the test session and write the summary.

        Args:
            success: Whether the goal was achieved.
            final_notes: Optional notes to include in the summary.

        Returns:
            Path to the generated report file.
        """
        duration = datetime.now() - self._start_time
        duration_str = str(duration).split(".")[0]  # Remove microseconds

        status_str = "PASSED" if success else "INCOMPLETE"

        summary = f"""## Session Summary

**Status:** {status_str}
**Total Steps:** {self._step_count}
**Duration:** {duration_str}
"""

        if self._ux_issues:
            summary += f"\n### UX Issues Found ({len(self._ux_issues)})\n\n"
            for issue in self._ux_issues:
                status_icon = "Warning" if issue["status"] == "WARN" else "Error"
                summary += f"- **Step {issue['step']}** ({status_icon}): {issue['issue']}\n"

        if final_notes:
            summary += f"\n### Notes\n\n{final_notes}\n"

        summary += f"\n---\n*Report generated by GhostBot*\n"

        self._write(summary)

        return str(self.filepath)

    def _write(self, content: str, mode: str = "a") -> None:
        """Write content to the report file."""
        with open(self.filepath, mode, encoding="utf-8") as f:
            f.write(content)

    @property
    def step_count(self) -> int:
        """Return the current step count."""
        return self._step_count

    @property
    def report_path(self) -> str:
        """Return the path to the report file."""
        return str(self.filepath)
