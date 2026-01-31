#!/usr/bin/env python3
"""
GhostBot - AI Mobile QA & UX Auditor Agent

Main entry point and orchestration loop.
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from core import MobileDriver, AIBrain, TestReporter, encode_image

# Load environment variables
load_dotenv()

console = Console()

# Constants
SCREENSHOT_PATH = Path("temp_screenshot.png")
MAX_STEPS = 50  # Safety limit to prevent infinite loops
UI_SETTLE_TIME = 2.0  # Seconds to wait for UI to settle
HIGH_LATENCY_THRESHOLD = 5000  # Milliseconds


def print_banner() -> None:
    """Print the GhostBot banner."""
    banner = """
   _____ _               _   ____        _
  / ____| |             | | |  _ \\      | |
 | |  __| |__   ___  ___| |_| |_) | ___ | |_
 | | |_ | '_ \\ / _ \\/ __| __|  _ < / _ \\| __|
 | |__| | | | | (_) \\__ \\ |_| |_) | (_) | |_
  \\_____|_| |_|\\___/|___/\\__|____/ \\___/ \\__|

    AI Mobile QA & UX Auditor Agent
    """
    console.print(Panel(banner, style="bold cyan"))


def execute_action(driver: MobileDriver, action: dict) -> bool:
    """
    Execute an action on the mobile device.

    Args:
        driver: The MobileDriver instance.
        action: Action dict with 'type' and optional 'value', 'x', 'y'.

    Returns:
        True if action was executed successfully.
    """
    action_type = action.get("type", "").lower()
    value = action.get("value", "")

    if action_type == "tap":
        console.print(f"[yellow]Tapping:[/yellow] '{value}'")
        return driver.tap(value)

    elif action_type == "tap_point":
        x, y = action.get("x", 0), action.get("y", 0)
        console.print(f"[yellow]Tapping point:[/yellow] ({x}, {y})")
        return driver.tap_point(x, y)

    elif action_type == "input":
        console.print(f"[yellow]Entering text:[/yellow] '{value}'")
        return driver.input_text(value)

    elif action_type == "back":
        console.print("[yellow]Pressing back button[/yellow]")
        return driver.go_back()

    elif action_type == "swipe":
        console.print(f"[yellow]Swiping:[/yellow] {value}")
        return driver.swipe(value)

    elif action_type == "wait":
        console.print("[yellow]Waiting for UI to settle...[/yellow]")
        time.sleep(UI_SETTLE_TIME)
        return True

    elif action_type == "done":
        console.print("[green]Goal achieved![/green]")
        return True

    else:
        console.print(f"[red]Unknown action type:[/red] {action_type}")
        return False


def run_ghost_bot(goal: str) -> None:
    """
    Run the GhostBot test session.

    Args:
        goal: The goal to achieve in this test session.
    """
    # Initialize components
    driver = MobileDriver()
    brain = AIBrain()
    reporter = TestReporter(output_dir="reports")

    console.print(f"[dim]Model: {brain.model}[/dim]")
    console.print(f"\n[bold]Goal:[/bold] {goal}\n")
    reporter.start_session(goal)

    step = 0
    goal_achieved = False
    last_action_time = time.time()

    try:
        while step < MAX_STEPS and not goal_achieved:
            step += 1
            console.rule(f"[bold]Step {step}[/bold]")

            # Capture screenshot
            console.print("[dim]Capturing screen...[/dim]")
            if not driver.capture_screen(str(SCREENSHOT_PATH)):
                console.print("[red]Failed to capture screenshot. Retrying...[/red]")
                time.sleep(1)
                continue

            # Optimize image for API
            console.print("[dim]Optimizing image...[/dim]")
            try:
                screenshot_b64 = encode_image(SCREENSHOT_PATH)
            except Exception as e:
                console.print(f"[red]Failed to encode image:[/red] {e}")
                continue

            # Get UI hierarchy
            console.print("[dim]Getting UI hierarchy...[/dim]")
            xml_hierarchy = driver.get_hierarchy()

            # Check for high latency
            current_time = time.time()
            latency_ms = int((current_time - last_action_time) * 1000)
            context = None
            if latency_ms > HIGH_LATENCY_THRESHOLD:
                context = f"HIGH LATENCY DETECTED: {latency_ms}ms since last action. The app may be slow or unresponsive."
                console.print(f"[yellow]Warning: High latency detected ({latency_ms}ms)[/yellow]")

            # Get AI decision
            console.print("[dim]Analyzing with AI...[/dim]")
            try:
                decision = brain.get_next_action(
                    screenshot_b64=screenshot_b64,
                    goal=goal,
                    xml_hierarchy=xml_hierarchy,
                    context=context,
                )
            except ValueError as e:
                console.print(f"[red]AI returned invalid response:[/red] {e}")
                console.print("[yellow]Retrying...[/yellow]")
                continue
            except Exception as e:
                console.print(f"[red]AI API error:[/red] {e}")
                console.print("[yellow]Retrying in 5 seconds...[/yellow]")
                time.sleep(5)
                continue

            # Extract decision components
            reasoning = decision.get("reasoning", "No reasoning provided")
            action = decision.get("action", {"type": "wait"})
            ux_audit = decision.get("ux_audit", {"status": "PASS", "issue": None})
            goal_achieved = decision.get("goal_achieved", False)

            # Display decision
            console.print(f"\n[bold]Reasoning:[/bold] {reasoning}")
            console.print(f"[bold]Action:[/bold] {action}")

            ux_status = ux_audit.get("status", "PASS")
            if ux_status == "PASS":
                console.print(f"[bold]UX Status:[/bold] [green]{ux_status}[/green]")
            elif ux_status == "WARN":
                console.print(f"[bold]UX Status:[/bold] [yellow]{ux_status} - {ux_audit.get('issue')}[/yellow]")
            else:
                console.print(f"[bold]UX Status:[/bold] [red]{ux_status} - {ux_audit.get('issue')}[/red]")

            # Log step to report
            reporter.log_step(
                action=action,
                reasoning=reasoning,
                ux_audit=ux_audit,
                latency_ms=latency_ms,
            )

            # Execute action
            if not goal_achieved:
                success = execute_action(driver, action)
                if not success:
                    console.print("[yellow]Action may have failed, continuing...[/yellow]")

                # Wait for UI to settle
                time.sleep(UI_SETTLE_TIME)

            last_action_time = time.time()

        # Session complete
        if goal_achieved:
            console.print("\n[bold green]Test Complete - Goal Achieved![/bold green]")
        else:
            console.print(f"\n[bold yellow]Test stopped after {MAX_STEPS} steps (limit reached)[/bold yellow]")

        # End session and save report
        report_path = reporter.end_session(
            success=goal_achieved,
            final_notes=f"Session ended after {step} steps."
        )
        console.print(f"\n[bold]Report saved:[/bold] {report_path}")

    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted by user[/yellow]")
        report_path = reporter.end_session(
            success=False,
            final_notes="Session interrupted by user."
        )
        console.print(f"\n[bold]Report saved:[/bold] {report_path}")

    finally:
        # Cleanup
        if SCREENSHOT_PATH.exists():
            SCREENSHOT_PATH.unlink()


def check_api_key() -> str:
    """
    Check for required API key based on configured provider.

    Returns:
        The provider name being used.
    """
    provider = os.getenv("AI_PROVIDER", "openai").lower()

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[red]Error: OPENAI_API_KEY not set[/red]")
            console.print("Please set your OpenAI API key in a .env file or environment variable.")
            console.print("See .env.example for reference.")
            sys.exit(1)
        return "OpenAI"
    elif provider in ("anthropic", "claude"):
        if not os.getenv("ANTHROPIC_API_KEY"):
            console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
            console.print("Please set your Anthropic API key in a .env file or environment variable.")
            console.print("See .env.example for reference.")
            sys.exit(1)
        return "Anthropic (Claude)"
    else:
        console.print(f"[red]Error: Unknown AI_PROVIDER '{provider}'[/red]")
        console.print("Supported providers: 'openai', 'anthropic'")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    print_banner()

    # Check for API key
    provider_name = check_api_key()
    console.print(f"[dim]Using AI provider: {provider_name}[/dim]\n")

    # Get goal from user
    console.print("\n[bold]Enter your test goal:[/bold]")
    console.print("[dim]Examples:[/dim]")
    console.print("  - Login with user@test.com and password 'test123'")
    console.print("  - Navigate to settings and enable dark mode")
    console.print("  - Add an item to cart and proceed to checkout\n")

    goal = Prompt.ask("[bold cyan]Goal[/bold cyan]")

    if not goal.strip():
        console.print("[red]Error: Goal cannot be empty[/red]")
        sys.exit(1)

    run_ghost_bot(goal.strip())


if __name__ == "__main__":
    main()
