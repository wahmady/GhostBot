#!/usr/bin/env python3
"""
GhostBot Setup Check

Verifies that all required tools (ADB, Maestro) are available
and a device is connected.
"""

import shutil
import subprocess
import sys


def check_command_exists(command: str) -> bool:
    """Check if a command is available in PATH."""
    return shutil.which(command) is not None


def check_adb_device() -> tuple[bool, str]:
    """
    Check if an Android device is connected via ADB.

    Returns:
        Tuple of (is_connected, device_info).
    """
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = result.stdout.strip().split("\n")

        # Filter out header and empty lines
        devices = [
            line for line in lines[1:]
            if line.strip() and "device" in line
        ]

        if devices:
            return True, devices[0].split("\t")[0]
        return False, "No device connected"

    except FileNotFoundError:
        return False, "ADB not installed"
    except subprocess.TimeoutExpired:
        return False, "ADB timed out"
    except Exception as e:
        return False, str(e)


def check_maestro_version() -> tuple[bool, str]:
    """
    Check Maestro version.

    Returns:
        Tuple of (is_available, version_info).
    """
    try:
        result = subprocess.run(
            ["maestro", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            return True, version
        return False, "Unknown error"

    except FileNotFoundError:
        return False, "Not installed"
    except subprocess.TimeoutExpired:
        return False, "Timed out"
    except Exception as e:
        return False, str(e)


def main() -> int:
    """Run all setup checks and print results."""
    print("\n" + "=" * 50)
    print("  GhostBot Setup Check")
    print("=" * 50 + "\n")

    all_passed = True

    # Check ADB
    print("Checking ADB...")
    if check_command_exists("adb"):
        print("  [OK] ADB is installed")
    else:
        print("  [X] ADB is NOT installed")
        print("      Install Android SDK Platform Tools")
        all_passed = False

    # Check ADB device
    print("\nChecking for connected device...")
    device_connected, device_info = check_adb_device()
    if device_connected:
        print(f"  [OK] Device connected: {device_info}")
    else:
        print(f"  [X] No device: {device_info}")
        print("      Connect a device via USB or start an emulator")
        all_passed = False

    # Check Maestro
    print("\nChecking Maestro...")
    maestro_ok, maestro_info = check_maestro_version()
    if maestro_ok:
        print(f"  [OK] Maestro installed: {maestro_info}")
    else:
        print(f"  [X] Maestro: {maestro_info}")
        print("      Install from: https://maestro.mobile.dev")
        all_passed = False

    # Check Python packages
    print("\nChecking Python packages...")
    required_packages = ["openai", "PIL", "dotenv", "tenacity", "rich"]
    package_names = ["openai", "pillow", "python-dotenv", "tenacity", "rich"]

    for pkg, name in zip(required_packages, package_names):
        try:
            if pkg == "PIL":
                __import__("PIL")
            elif pkg == "dotenv":
                __import__("dotenv")
            else:
                __import__(pkg)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [X] {name} - run: pip install {name}")
            all_passed = False

    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("  [OK] All checks passed! GhostBot is ready to run.")
        print("=" * 50 + "\n")
        return 0
    else:
        print("  [X] Some checks failed. Please fix the issues above.")
        print("=" * 50 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
