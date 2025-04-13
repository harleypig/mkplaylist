# `pre-commit` Hooks Guide

This guide explains how to run each `pre-commit` hook manually from the command
line for debugging purposes. There are two configurations available:

1. **Default Configuration** (`.pre-commit-config.yaml`): Checks code without making changes
2. **With-Fixes Configuration** (`.pre-commit-config-with-fixes.yaml`): Can modify code to fix issues

## Running `pre-commit`

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

## Hook Categories

### Custom Local Hooks

These hooks are implemented locally in the repository and have specific behavior.

#### no-commit-to-master

This hook prevents commits to the master/main branch. It behaves the same in
both configurations and will abort the commit process with an error message if
you try to commit directly to master/main.

```bash
./scripts/no-commit-to-master.sh
```

Note: This hook doesn't make any changes to files. It simply blocks the commit
if it's on a protected branch.

#### check-files

Checks for both trailing whitespace and missing final newlines without
modifying files.

This hook runs from the default configuration (`.pre-commit-config.yaml`).

```bash
./scripts/check-files.sh
```

Note: This custom hook was created because the standard trailing-whitespace and
end-of-file-fixer hooks don't have check-only options. This hook only reports issues
without modifying files.

### Validation-Only Hooks

These hooks only check for issues and never modify files in either configuration.

See the `Running pre-commit` section above for details on how to run these
hooks via `pre-commit`.

#### check-yaml
Validates YAML files.

**Direct command:**
```bash
find . -name "*.yaml" -o -name "*.yml" | xargs yamllint
```

#### check-added-large-files
Prevents large files from being committed.

**Direct command:**
```bash
find . -type f -not -path "*/\.*" -not -path "*/venv/*" -size +500k
```

#### check-toml
Validates TOML files.

**Direct command:**
```bash
find . -name "*.toml" | xargs python -c "import tomli; [tomli.loads(open(f).read()) for f in __import__('sys').argv[1:]]"
```

#### check-merge-conflict
Checks for files containing merge conflict strings.

**Direct command:**
```bash
grep -l "<<<<<<< HEAD" $(find . -type f -not -path "*/\.*" -not -path "*/venv/*")
```

#### debug-statements
Checks for debugger imports and py37+ `breakpoint()` calls.

**Direct command:**
```bash
grep -r "import pdb\|import ipdb\|breakpoint()" --include="*.py" .
```

#### check-case-conflict
Checks for files with names that would conflict on a case-insensitive
filesystem.


#### flake8
Lints Python files with flake8.

**Direct command:**
```bash
flake8 .
```

Note: flake8 doesn't automatically fix issues in either configuration.

#### mypy
Type-checks Python code.

**Direct command:**
```bash
mypy --no-strict-optional --ignore-missing-imports .
```

Note: mypy doesn't automatically fix issues in either configuration.

### Check-Only in Default, Fix in With-Fixes

These hooks check for issues in the default configuration but can modify files
to fix issues when run with the with-fixes configuration.

#### trailing-whitespace (with-fixes only)
Removes trailing whitespace at the end of lines.

**With fixes (will modify files):**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml trailing-whitespace --all-files
```

**Direct command (with fixes):**
```bash
find . -type f -not -path "*/\.*" -not -path "*/venv/*" | xargs sed -i 's/[[:space:]]*$//'
```

#### end-of-file-fixer (with-fixes only)
Ensures files end with a newline by modifying them.

**With fixes (will modify files):**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml end-of-file-fixer --all-files
```

**Direct command (with fixes):**
```bash
find . -type f -not -path "*/\.*" -not -path "*/venv/*" -exec sh -c 'if [ -n "$(tail -c 1 "{}")" ]; then echo >> "{}"; fi' \;
```

#### isort
Sorts Python imports.

**Default (check only):**
```bash
isort --check --jobs=-1 .
```

**With fixes:**
```bash
isort --jobs=-1 .
```

#### black
Formats Python code.

**Default (check only):**
```bash
black --check --diff .
```

**With fixes:**
```bash
black .
```

#### pyupgrade (with-fixes only)
Upgrades Python syntax to newer versions.

**With fixes:**
```bash
pre-commit run --config .pre-commit-config-with-fixes.yaml pyupgrade --all-files
```

**Direct command:**
```bash
find . -name "*.py" | xargs pyupgrade --py38-plus
```

#### ruff (with-fixes only)
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
