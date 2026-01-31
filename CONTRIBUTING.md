# Contributing to GhostBot

Thank you for your interest in contributing to GhostBot! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- A clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behavior
- Your environment (OS, Python version, device type)
- Relevant logs or screenshots

### Suggesting Features

Feature requests are welcome! Please open an issue with:

- A clear description of the feature
- The problem it solves or use case it enables
- Any implementation ideas you have

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Test your changes** thoroughly
4. **Commit with clear messages** describing what and why
5. **Open a pull request** with a description of your changes

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/GhostBot.git
   cd GhostBot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   cd ghostbot
   pip install -r requirements.txt
   ```

4. Copy and configure environment:
   ```bash
   cp .env.example .env
   # Add your API keys
   ```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public classes and functions
- Keep functions focused and reasonably sized

### Example

```python
def process_screenshot(image_path: str, max_size: int = 1024) -> str:
    """
    Process and encode a screenshot for API submission.

    Args:
        image_path: Path to the screenshot file.
        max_size: Maximum dimension in pixels.

    Returns:
        Base64 encoded image string.
    """
    # Implementation here
```

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (Add, Fix, Update, Remove)
- Keep the first line under 72 characters
- Add details in the body if needed

Examples:
- `Add support for iOS device testing`
- `Fix screenshot capture timeout on slow devices`
- `Update documentation for Claude model configuration`

## Project Structure

When adding new features, follow the existing structure:

- `core/driver.py` - Device interaction and automation
- `core/brain.py` - AI model integration
- `core/optimizer.py` - Image processing
- `core/logger.py` - Report generation
- `core/prompts.py` - AI system prompts

## Testing

Before submitting:

1. Run `setup_check.py` to verify environment
2. Test with both OpenAI and Anthropic providers if possible
3. Test on an actual mobile device
4. Verify reports are generated correctly

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.

## License

By contributing to GhostBot, you agree that your contributions will be licensed under the MIT License.
