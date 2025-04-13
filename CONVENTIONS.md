# Project Conventions

This document outlines the coding conventions and standards for the mkplaylist
project. Following these guidelines ensures consistency across the codebase
and makes collaboration easier.

## Code Style

### Python

- **Indentation**: 2 spaces
- **Line Length**: 79 characters maximum
- **Naming**:
  - Classes: `CamelCase`
  - Functions/Methods: `snake_case`
  - Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Docstrings**: Google style docstrings
- **Imports**: Follow the order specified in `.isort.cfg`
  - This can be loosely followed; as long as isort runs successfully, you
      should be ok.

### Configuration Files

Always honor existing configuration files for code formatting and linting
tools:

- **YAPF**: Use `.style.yapf` for Python code formatting
- **isort**: Use `.isort.cfg` for import sorting
- **flake8**: Use `.flake8` for linting

Any other configuration files should be honored too, but be careful of
overlapping and conflicting settings.

## Git Workflow

- Create feature branches from `master`
- Use descriptive branch names (e.g., `feature/add-spotify-integration`)
- Write clear commit messages that explain the "why" not just the "what"; use
    the [Conventional Commits](https://www.conventionalcommits.org/en)
    specification
- Keep commits focused on a single logical change
- Rebase feature branches on `master` before submitting pull requests

## Pull Requests

- Keep PRs focused on a single feature or bug fix
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass before requesting review

## Testing

- Write unit tests for all new functionality
- Maintain test coverage above 80%
- Use pytest for running tests
- Mock external dependencies in unit tests

## Documentation

- Keep README.md up to date
- Document public APIs with docstrings
- Update user documentation when adding or changing features
- Use Markdown for documentation files

## Dependencies

- Add new dependencies only when necessary
- Document the purpose of each dependency in requirements.txt
- Keep development dependencies separate in requirements-dev.txt

## Pre-commit Hooks

Use pre-commit hooks to ensure code quality before committing:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Configuration

- Follow the XDG Base Directory Specification for file locations
- Use environment variables for configuration when appropriate
- Document all configuration options

## Error Handling

- Use specific exception types
- Log exceptions with appropriate context
- Provide user-friendly error messages

## Code Organization

- Keep modules focused on a single responsibility
- Use appropriate abstraction layers
- Follow the project's existing architecture patterns
