# Pre-commit Hooks Guide

This guide explains how to run each pre-commit hook manually from the command line for debugging purposes. There are two configurations available:

1. **Default Configuration** (`.pre-commit-config.yaml`): Checks code without making changes
2. **With-Fixes Configuration** (`.pre-commit-config-with-fixes.yaml`): Can modify code to fix issues

## Running Pre-commit

### All Hooks

**Default (check only):**
```bash
pre-commit run --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml --all-files
```

### Single Hook

**Default (check only):**
```bash
pre-commit run <hook-id> --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml <hook-id> --all-files
```

## Hook-Specific Commands

### no-commit-to-master

This hook prevents commits to the master/main branch. It behaves the same in both configurations and will abort the commit process with an error message if you try to commit directly to master/main.

**Default:**
```bash
./scripts/no-commit-to-master.sh
```

**With fixes:**
```bash
./scripts/no-commit-to-master.sh
```

Note: This hook doesn't make any changes to files. It simply blocks the commit if it's on a protected branch.

### trailing-whitespace

Removes trailing whitespace at the end of lines.

**Default (check only):**
```bash
pre-commit run trailing-whitespace --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml trailing-whitespace --all-files
```

**Direct command (with fixes):**
```bash
find . -type f -not -path "*/\.*" -not -path "*/venv/*" | xargs sed -i 's/[[:space:]]*$//'
```

### end-of-file-fixer

Ensures files end with a newline.

**Default (check only):**
```bash
pre-commit run end-of-file-fixer --all-files
```

**Direct command:**
```bash
find . -type f -not -path "*/\.*" -not -path "*/venv/*" -exec sh -c 'if [ -n "$(tail -c 1 "{}")" ]; then echo >> "{}"; fi' \;
```

### check-yaml

Validates YAML files.

**Default:**
```bash
pre-commit run check-yaml --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml check-yaml --all-files
```

**Direct command:**
```bash
find . -name "*.yaml" -o -name "*.yml" | xargs yamllint
```

### check-added-large-files

Prevents large files from being committed.

**Default:**
```bash
pre-commit run check-added-large-files --all-files
```

**Direct command:**
```bash
find . -type f -not -path "*/\.*" -not -path "*/venv/*" -size +500k
```

### check-toml

Validates TOML files.

**Default:**
```bash
pre-commit run check-toml --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml check-toml --all-files
```

**Direct command:**
```bash
find . -name "*.toml" | xargs python -c "import tomli; [tomli.loads(open(f).read()) for f in __import__('sys').argv[1:]]"
```

### check-merge-conflict

Checks for files containing merge conflict strings.

**Default:**
```bash
pre-commit run check-merge-conflict --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml check-merge-conflict --all-files
```

**Direct command:**
```bash
grep -l "<<<<<<< HEAD" $(find . -type f -not -path "*/\.*" -not -path "*/venv/*")
```

### debug-statements

Checks for debugger imports and py37+ `breakpoint()` calls.

**Default:**
```bash
pre-commit run debug-statements --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml debug-statements --all-files
```

**Direct command:**
```bash
grep -r "import pdb\|import ipdb\|breakpoint()" --include="*.py" .
```

### check-case-conflict

Checks for files with names that would conflict on a case-insensitive filesystem.

**Default:**
```bash
pre-commit run check-case-conflict --all-files
```

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml check-case-conflict --all-files
```

### flake8

Lints Python files with flake8.

**Default (check only):**
```bash
flake8 .
```

**With fixes (check only):**
```bash
flake8 .
```

Note: flake8 doesn't automatically fix issues in either configuration.

### isort

Sorts Python imports.

**Default (check only):**
```bash
isort --check --jobs=-1 .
```

**With fixes:**
```bash
isort --jobs=-1 .
```

### black

Formats Python code.

**Default (check only):**
```bash
black --check --diff .
```

**With fixes:**
```bash
black .
```

### mypy

Type-checks Python code.

**Default (check only):**
```bash
mypy --no-strict-optional --ignore-missing-imports .
```

**With fixes (check only):**
```bash
mypy --no-strict-optional --ignore-missing-imports .
```

Note: mypy doesn't automatically fix issues in either configuration.

### pyupgrade (with-fixes only)

Upgrades Python syntax to newer versions.

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml pyupgrade --all-files
```

**Direct command:**
```bash
find . -name "*.py" | xargs pyupgrade --py38-plus
```

### ruff (with-fixes only)

Fast Python linter with automatic fixes.

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml ruff --all-files
```

**Direct command:**
```bash
ruff check --fix .
```

## Tips for Debugging

1. Run specific hooks on specific files:
   ```bash
   pre-commit run <hook-id> --files path/to/file.py
   ```

2. Skip specific hooks:
   ```bash
   SKIP=flake8,black pre-commit run --all-files
   ```

3. Run hooks manually without git:
   ```bash
   pre-commit run --files path/to/file.py
   ```

4. See verbose output:
   ```bash
   pre-commit run --verbose <hook-id> --files path/to/file.py
   ```
