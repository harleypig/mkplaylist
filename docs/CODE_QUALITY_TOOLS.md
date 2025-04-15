# Code Quality Tools

This document describes the code quality tools used in this project, how to install them, and where their configuration files are located.

## Purpose

The purpose of this document is to:

1. **Document the tools** used for maintaining code quality in this project
2. **Provide installation instructions** for developers to set up their environment
3. **Explain the configuration** of each tool and where to find the configuration files
4. **Describe the workflow** for using these tools effectively

We follow the Unix philosophy of "do one thing and do it well" by using specialized tools for different aspects of code quality rather than a single all-in-one solution.

## Installation

You can install all the required code quality tools using pip:

```bash
# Install all development dependencies including code quality tools
pip install -r requirements-dev.txt
```

This will install the following code quality tools:
- flake8: For linting
- isort: For import sorting
- yapf: For code formatting
- mypy: For type checking
- pre-commit: For running checks before committing

## Configuration Files

Each tool has its own configuration file:

| Tool | Configuration File | Purpose |
|------|-------------------|---------|
| flake8 | `.flake8` | Linting rules and error codes |
| isort | `.isort.cfg` | Import sorting configuration |
| yapf | `.style.yapf` | Code formatting rules |
| mypy | `mypy.ini` (implicit) | Type checking configuration |
| pre-commit | `.pre-commit-config.yaml` | Pre-commit hook configuration |
| pre-commit (with fixes) | `.pre-commit-config-with-fixes.yaml` | Auto-fixing pre-commit configuration |

## Tool Descriptions

### Linting

**flake8** is a code linter that checks Python code for style and programming errors, enforcing PEP 8 style guide.

- Configuration: `.flake8`
- Usage: `flake8 .`
- Purpose: Identifies style issues and potential bugs without modifying code

### Import Sorting

**isort** automatically sorts and formats import statements according to PEP 8 guidelines.

- Configuration: `.isort.cfg`
- Usage: `isort --check .` (check only) or `isort .` (fix)
- Purpose: Organizes imports into sections and sorts them alphabetically

### Code Formatting

**yapf** (Yet Another Python Formatter) reformats code to ensure consistent style.

- Configuration: `.style.yapf`
- Usage: `yapf --diff --recursive .` (check only) or `yapf --in-place --recursive .` (fix)
- Purpose: Ensures consistent code formatting throughout the codebase

### Type Checking

**mypy** is a static type checker for Python that helps catch certain classes of bugs.

- Configuration: Implicit or via `mypy.ini`
- Usage: `mypy --no-strict-optional --ignore-missing-imports .`
- Purpose: Verifies type consistency based on type annotations

## Workflow

We use a two-stage approach to code quality:

1. **Check-only mode**: Used during pre-commit hooks to prevent committing code with issues
   ```bash
   pre-commit run --all-files
   ```

2. **Fix mode**: Used manually to automatically fix issues before committing
   ```bash
   pre-commit run --config .pre-commit-config-with-fixes.yaml --all-files
   ```

For more details on running the pre-commit hooks, see [pre-commit.md](../pre-commit.md).

## CI/CD Integration

These tools are also integrated into our CI/CD pipeline to ensure code quality standards are maintained across all contributions.

## Adding New Tools

When adding new code quality tools to the project:

1. Add the tool to `requirements-dev.txt`
2. Create appropriate configuration files
3. Update the pre-commit configuration files
4. Document the tool in this file
