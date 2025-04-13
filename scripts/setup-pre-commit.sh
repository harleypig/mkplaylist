#!/bin/bash
# setup-pre-commit.sh - Install pre-commit hooks for mkplaylist
#
# This script installs pre-commit hooks using the default configuration
# that only checks code without making changes. It also provides instructions
# for using the secondary configuration that can modify code.

# Exit on error
set -e

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Error: pre-commit is not installed."
    echo "Please install it using: pip install pre-commit"
    echo "Or if you have requirements-dev.txt: pip install -r requirements-dev.txt"
    exit 1
fi

# Get the project root directory (where .git is located)
ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Error: This script must be run from within a git repository."
    exit 1
fi

# Check if the default pre-commit config exists
if [ ! -f "$ROOT_DIR/.pre-commit-config.yaml" ]; then
    echo "Error: .pre-commit-config.yaml not found in the project root."
    echo "Please make sure you're running this script from the project directory."
    exit 1
fi

# Check if the secondary pre-commit config exists
if [ ! -f "$ROOT_DIR/.pre-commit-config-with-fixes.yaml" ]; then
    echo "Warning: .pre-commit-config-with-fixes.yaml not found in the project root."
    echo "The secondary configuration for making fixes will not be available."
fi

# Check if the no-commit-to-master hook script exists and make it executable
if [ -f "$ROOT_DIR/scripts/no-commit-to-master.sh" ]; then
    chmod +x "$ROOT_DIR/scripts/no-commit-to-master.sh"
    echo "Made scripts/no-commit-to-master.sh executable."
else
    echo "Warning: scripts/no-commit-to-master.sh not found."
    echo "The branch protection hook will not be available."
fi

echo "Installing pre-commit hooks with the default configuration..."
cd "$ROOT_DIR"
pre-commit install

echo "Pre-commit hooks installed successfully!"
echo ""
echo "The default configuration will run automatically on git commit and will only check code without making changes."
echo ""
echo "To run the checks manually on all files:"
echo "  pre-commit run --all-files"
echo ""

if [ -f "$ROOT_DIR/.pre-commit-config-with-fixes.yaml" ]; then
    echo "To use the secondary configuration that can modify code:"
    echo "  pre-commit run --config .pre-commit-config-with-fixes.yaml --all-files"
    echo ""
    echo "To run the secondary configuration on specific files:"
    echo "  pre-commit run --config .pre-commit-config-with-fixes.yaml --files file1.py file2.py"
    echo ""
    echo "Note: The secondary configuration will modify your files to fix issues."
    echo "      It should be run manually before committing, not as part of the git commit process."
fi

if [ -f "$ROOT_DIR/scripts/no-commit-to-master.sh" ]; then
    echo ""
    echo "Branch Protection:"
    echo "  The no-commit-to-master hook will prevent direct commits to master/main branches."
    echo "  This encourages proper git workflow using feature branches and pull requests."
    echo ""
    echo "  To bypass this protection in exceptional cases:"
    echo "    git commit --no-verify"
    echo ""
    echo "  Or temporarily disable all hooks:"
    echo "    git -c core.hooksPath=/dev/null commit"
fi

echo "Happy coding!"
