"""
GhostBot Mobile Driver

Wrapper for Maestro and ADB subprocess calls to control mobile devices.
"""

import subprocess
from typing import Optional

from rich.console import Console

console = Console()


class MobileDriver:
    """
    MobileDriver provides an interface to control Android devices
    using ADB and Maestro CLI commands.
    """

    def __init__(self) -> None:
        """Initialize the MobileDriver."""
        self._last_error: Optional[str] = None

    @property
    def last_error(self) -> Optional[str]:
        """Return the last error message, if any."""
        return self._last_error

    def _run_command(
        self, command: list[str], capture_output: bool = True
    ) -> tuple[bool, str]:
        """
        Execute a subprocess command safely.

        Args:
            command: List of command arguments.
            capture_output: Whether to capture stdout/stderr.

        Returns:
            Tuple of (success, output/error message).
        """
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                self._last_error = None
                return True, result.stdout
            else:
                self._last_error = result.stderr or f"Command failed with code {result.returncode}"
                console.print(f"[red]Error:[/red] {self._last_error}")
                return False, self._last_error
        except subprocess.TimeoutExpired:
            self._last_error = "Command timed out after 30 seconds"
            console.print(f"[red]Error:[/red] {self._last_error}")
            return False, self._last_error
        except FileNotFoundError as e:
            self._last_error = f"Command not found: {e.filename}"
            console.print(f"[red]Error:[/red] {self._last_error}")
            return False, self._last_error
        except Exception as e:
            self._last_error = str(e)
            console.print(f"[red]Error:[/red] {self._last_error}")
            return False, self._last_error

    def capture_screen(self, path: str) -> bool:
        """
        Capture a screenshot from the connected device.

        Uses ADB's screencap which is faster than Maestro's built-in screenshot.

        Args:
            path: File path to save the screenshot.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(path, "wb") as f:
                result = subprocess.run(
                    ["adb", "exec-out", "screencap", "-p"],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    timeout=10,
                )
            if result.returncode == 0:
                self._last_error = None
                return True
            else:
                self._last_error = result.stderr.decode() if result.stderr else "Screenshot failed"
                console.print(f"[red]Error capturing screen:[/red] {self._last_error}")
                return False
        except Exception as e:
            self._last_error = str(e)
            console.print(f"[red]Error capturing screen:[/red] {self._last_error}")
            return False

    def get_hierarchy(self) -> Optional[str]:
        """
        Get the UI hierarchy XML from the device via Maestro.

        Returns:
            XML string of the UI hierarchy, or None on failure.
        """
        success, output = self._run_command(["maestro", "hierarchy"])
        if success:
            return output
        return None

    def tap(self, text: str) -> bool:
        """
        Tap on an element by its text content.

        Args:
            text: The text of the element to tap.

        Returns:
            True if successful, False otherwise.
        """
        success, _ = self._run_command(["maestro", "studio", "tap", text])
        return success

    def tap_point(self, x: int, y: int) -> bool:
        """
        Tap on a specific screen coordinate.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if successful, False otherwise.
        """
        success, _ = self._run_command(
            ["maestro", "studio", "tap", "-x", str(x), "-y", str(y)]
        )
        return success

    def input_text(self, text: str) -> bool:
        """
        Input text into the currently focused field.

        Args:
            text: The text to input.

        Returns:
            True if successful, False otherwise.
        """
        success, _ = self._run_command(["maestro", "studio", "input", text])
        return success

    def go_back(self) -> bool:
        """
        Press the back button on the device.

        Returns:
            True if successful, False otherwise.
        """
        success, _ = self._run_command(["adb", "shell", "input", "keyevent", "4"])
        return success

    def swipe(self, direction: str) -> bool:
        """
        Swipe in a direction on the device.

        Args:
            direction: One of 'up', 'down', 'left', 'right'.

        Returns:
            True if successful, False otherwise.
        """
        swipe_coords = {
            "up": (500, 1500, 500, 500),
            "down": (500, 500, 500, 1500),
            "left": (800, 1000, 200, 1000),
            "right": (200, 1000, 800, 1000),
        }
        if direction not in swipe_coords:
            self._last_error = f"Invalid swipe direction: {direction}"
            return False

        x1, y1, x2, y2 = swipe_coords[direction]
        success, _ = self._run_command(
            ["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), "300"]
        )
        return success

    def launch_app(self, package: str) -> bool:
        """
        Launch an application by its package name.

        Args:
            package: The package name (e.g., 'com.example.app').

        Returns:
            True if successful, False otherwise.
        """
        success, _ = self._run_command(
            ["adb", "shell", "monkey", "-p", package, "-c",
             "android.intent.category.LAUNCHER", "1"]
        )
        return success
