# GhostBot - Project Specification: AI Mobile QA & UX Auditor Agent

## 1. Project Overview
We are building an autonomous "AI User" that tests mobile applications. GhostBot uses **Python** to orchestrate control, **Maestro** to drive the mobile device (via ADB/IDB), and **OpenAI GPT-4o** as the "Brain" to visually analyze screens and decide on actions.

**Key Capabilities:**
1.  **Autonomous Navigation:** Explores apps to achieve a goal (e.g., "Login and buy coffee").
2.  **UX Auditing:** Detects frustration signals (high latency, broken UI, rage clicks).
3.  **Reporting:** Generates a human-readable Markdown log of the session.

---

## 2. Tech Stack & Architecture
* **Language:** Python 3.10+
* **Mobile Driver:** Maestro (CLI tool), ADB (Android Debug Bridge)
* **AI Model:** OpenAI GPT-4o (Vision)
* **Image Processing:** Pillow (PIL) for token optimization
* **Configuration:** `python-dotenv` for security

**The Loop:**
`Capture Screen` -> `Optimize Image` -> `GPT-4o Analysis` -> `JSON Decision` -> `Execute Maestro Command` -> `Log Result`

---

## 3. Directory Structure
Please generate the following file structure. Do not create files not listed here unless necessary for Python packaging.

```text
ghostbot/
├── .env.example            # Template for API keys
├── requirements.txt        # Python dependencies
├── main.py                 # Entry point / Event loop
├── setup_check.py          # Script to verify ADB/Maestro availability
├── core/
│   ├── __init__.py
│   ├── driver.py           # Wrapper for Maestro and ADB subprocess calls
│   ├── brain.py            # OpenAI API interaction layer
│   ├── optimizer.py        # Image resizing and compression
│   ├── logger.py           # Handles Markdown report generation
│   └── prompts.py          # System prompts for the LLM
└── reports/                # Output directory for test logs (gitignored)
```

---

## 4. Implementation Details (Step-by-Step)

### Step 1: Dependencies (`requirements.txt`)

Include strict versioning for stability:

* `openai>=1.3.0`
* `pillow>=10.0.0`
* `python-dotenv>=1.0.0`
* `tenacity>=8.2.0` (For API retry logic)
* `rich>=13.0.0` (For pretty terminal output)

### Step 2: The Infrastructure (`core/driver.py`)

Create a class `MobileDriver` that wraps subprocess calls.

* **Function `capture_screen(path)`**: Use `adb exec-out screencap -p > path`. This is faster than Maestro's built-in screenshot.
* **Function `get_hierarchy()`**: Run `maestro hierarchy`. Return the XML string.
* **Function `tap(text)`**: Run `maestro studio tap <text>`.
* **Function `tap_point(x, y)`**: Run `maestro studio tap -x <x> -y <y>`.
* **Function `input_text(text)`**: Run `maestro studio input <text>`.
* **Function `go_back()`**: Run `adb shell input keyevent 4`.
* **Safety**: Wrap all subprocess calls in try/except blocks. If Maestro fails, print a clear error.

### Step 3: Image Optimization (`core/optimizer.py`)

Create a function `encode_image(image_path)`:

1. Open image with PIL.
2. Resize so the longest side is max **1024px** (preserves tokens).
3. Compress to JPEG with quality=85.
4. Return the base64 encoded string.

### Step 4: The Brain (`core/brain.py` & `core/prompts.py`)

* **`core/prompts.py`**:
    * Define a variable `SYSTEM_PROMPT`.
    * Instruction: "You are GhostBot, a Mobile QA Agent. Analyze the screen. Return JSON only."
    * Define the output schema strictly:
    ```json
    {
        "reasoning": "string",
        "action": {"type": "tap", "value": "Login"},
        "ux_audit": {"status": "PASS/FAIL", "issue": "string"},
        "goal_achieved": boolean
    }
    ```

* **`core/brain.py`**:
    * Class `AIBrain` with method `get_next_action(screenshot_b64, xml_hierarchy, goal)`.
    * Use `openai.chat.completions.create` with `model="gpt-4o"`.
    * Set `response_format={"type": "json_object"}`.
    * Use `tenacity` to retry on API timeouts.

### Step 5: Reporting (`core/logger.py`)

* Class `TestReporter`.
* Create a method `log_step(step_number, action, reasoning, ux_status)`.
* Append to a Markdown file in `reports/`.
* Format:
    ```markdown
    ## Step 1
    **Action:** Tapped 'Login'
    **Reasoning:** I see the login button...
    **UX Status:** Warning - High Latency (5s)
    ```

### Step 6: The Main Loop (`main.py`)

This is the critical orchestration layer.

1. **Setup**: Load `.env`, initialize `MobileDriver`, `AIBrain`, `TestReporter`.
2. **Input**: Ask user for a GOAL (e.g., "Login with user@test.com").
3. **Loop (While not goal_achieved)**:
    * `driver.capture_screen()`
    * `optimizer.encode_image()`
    * `driver.get_hierarchy()`
    * **UX Timer Check**: Measure time taken since last action. If > 5 seconds, inject "High Latency Detected" into the context sent to the AI.
    * `brain.get_next_action()`
    * `reporter.log_step()`
    * **Execute**: If action is 'tap', call `driver.tap()`.
    * Sleep 2 seconds to allow UI to settle.
4. **Exit**: Save report and print "Test Complete".

---

## 5. Environment & Setup Scripts

* **`setup_check.py`**:
    * Check if `adb` is in PATH.
    * Check if `maestro` is in PATH.
    * Check if a device is connected (`adb devices`).
    * Print status with emojis (check mark / X mark).

---

## 6. Rules for Code Generation

* **Docstrings**: Add docstrings to all major classes.
* **Error Handling**: If the AI returns invalid JSON, log the error and retry the loop (don't crash).
* **Type Hinting**: Use Python type hints (e.g., `def tap(self, text: str) -> None:`).
* **Maestro Syntax**: Ensure Maestro commands use the `maestro studio ...` syntax for ad-hoc commands, NOT `maestro test`.

---

## How to Use This Spec with Cursor

1. Open this folder in Cursor.
2. Open the Chat (Cmd+L / Ctrl+L).
3. Drag this file into the chat or `@` mention it.
4. Type: **"Read this spec file and generate the project structure and code exactly as described."**

Cursor will then systematically build the entire GhostBot tool for you, file by file.
