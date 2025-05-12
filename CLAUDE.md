# CLAUDE.md - Theatre Scraper Project Guide

## Build/Test Commands
- Run all tests: `pytest tests/`
- Run specific test file: `pytest tests/path/to/test_file.py`
- Run specific test: `pytest tests/path/to/test_file.py::TestClass::test_method`
- Run tests with verbose output: `pytest -v tests/`
- Check types: `mypy src/`
- Lint code: `flake8 src/`

## Code Style Guidelines
- **Imports**: Group imports (stdlib, 3rd party, local) with newlines between groups
- **Docstrings**: Use Google style docstrings with type annotations
- **Types**: Use type annotations for function parameters and return values
- **Error Handling**: Use try/except blocks with specific exceptions and meaningful error messages
- **Variable Names**: Use snake_case for variables and functions, CamelCase for classes
- **Constants**: Use UPPERCASE for constants
- **Model Classes**: Use dataclasses for data models with proper type annotations
- **Logging**: Use logger.info/debug/error with contextual information
- **Testing**: Test each module in dedicated test files with specific test cases