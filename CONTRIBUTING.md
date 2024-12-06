# Contributing to ai01

Thank you for your interest in contributing to ai01! This package aims to provide efficient AI tools and utilities for Python developers.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/Huddle01/huddle01-ai.git
   cd huddle01-ai
   ```
3. Make Sure you have Poetry installed:
   ```bash
   pip install poetry
   ```
4. Install dependencies:
   ```bash
    poetry install
    ```
5. Create a new branch:
    ```bash
    git checkout -b feature/your-feature
    # or
    git checkout -b fix/your-fix
    ```

## Development Guidelines

### Code Standards
- Use Python 3.12+
- Use type hints
- Add docstrings for all public functions/classes
- Keep functions focused and modular


### Pull Request Process

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   # or
   git checkout -b fix/your-fix
   ```

2. Make your changes following our code standards

3. Commit your changes:
   ```bash
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue"
   ```

4. Push to your fork and submit a Pull Request

### PR Requirements
- Clear description of changes
- Tests for new features
- Updated documentation if needed
- All tests passing
- Code follows project style

## Bug Reports

Create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version and ai01 version
- Code example demonstrating the issue

## Feature Requests

Create an issue with:
- Clear description of the feature
- Use case and benefits
- Example of how it would work
- Any implementation ideas

## Documentation

- Update docstrings for any modified code
- Add examples for new features
- Follow Google style docstrings:
  ```python
  def function(param: type) -> return_type:
      """Short description.

      Args:
          param: Parameter description.

      Returns:
          Description of return value.
      """
  ```

## Questions?

- Create an issue for any questions
- Check existing issues and discussions first

## License

By contributing, you agree that your contributions will be licensed under the project's BSD 3-Clause License.