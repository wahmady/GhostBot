# GhostBot

**AI Mobile QA & UX Auditor Agent**

GhostBot is an autonomous AI agent that tests mobile applications by simulating real user interactions. It uses vision-capable AI models to analyze screens, make intelligent decisions, and detect UX issues automatically.

## Features

- **Autonomous Navigation**: Explores mobile apps to achieve goals (e.g., "Login and buy coffee")
- **Visual AI Analysis**: Uses GPT-4o or Claude to understand and interact with app screens
- **UX Auditing**: Detects frustration signals like high latency, broken UI, and unresponsive elements
- **Detailed Reporting**: Generates human-readable Markdown logs of each test session
- **Multi-Provider Support**: Works with OpenAI (GPT-4o) or Anthropic (Claude) models

## Prerequisites

Before using GhostBot, ensure you have:

- Python 3.10 or higher
- [Maestro](https://maestro.mobile.dev/) CLI installed
- [ADB](https://developer.android.com/tools/adb) (Android Debug Bridge) for Android testing
- An API key for OpenAI or Anthropic

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/wahmady/GhostBot.git
   cd GhostBot
   ```

2. **Install Python dependencies**:
   ```bash
   cd ghostbot
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Verify setup**:
   ```bash
   python setup_check.py
   ```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# AI Provider: "openai" or "anthropic"
AI_PROVIDER=openai

# OpenAI (if using GPT-4o)
OPENAI_API_KEY=your_key_here

# Anthropic (if using Claude)
ANTHROPIC_API_KEY=your_key_here
```

## Usage

1. Connect your Android device via USB (with USB debugging enabled)
2. Run GhostBot:
   ```bash
   python main.py
   ```
3. Enter your test goal when prompted (e.g., "Login with test@example.com")
4. Watch as GhostBot autonomously navigates the app
5. Review the generated report in the `reports/` directory

### Example Goals

- "Login with user@test.com and password 'test123'"
- "Navigate to settings and enable dark mode"
- "Add an item to cart and proceed to checkout"
- "Find the help section and submit a feedback form"

## Project Structure

```
ghostbot/
├── .env.example          # Template for API keys
├── requirements.txt      # Python dependencies
├── main.py               # Entry point / Event loop
├── setup_check.py        # Verify ADB/Maestro availability
├── core/
│   ├── __init__.py
│   ├── driver.py         # Maestro and ADB wrapper
│   ├── brain.py          # AI interaction layer
│   ├── optimizer.py      # Image optimization
│   ├── logger.py         # Report generation
│   └── prompts.py        # System prompts for the LLM
└── reports/              # Output directory for test logs
```

## How It Works

GhostBot operates in a continuous loop:

1. **Capture Screen**: Takes a screenshot via ADB
2. **Optimize Image**: Resizes and compresses for API efficiency
3. **AI Analysis**: Sends the image to the AI model for analysis
4. **Decision Making**: AI returns a JSON decision with action and UX assessment
5. **Execute Action**: Performs the action via Maestro
6. **Log Results**: Records the step in the Markdown report

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Maestro](https://maestro.mobile.dev/) for mobile automation
- [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/) for AI capabilities
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
