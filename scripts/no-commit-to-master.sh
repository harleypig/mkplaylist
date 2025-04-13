#!/bin/bash
# no-commit-to-master.sh - Prevent direct commits to master/main branch
#
# This pre-commit hook checks if the current branch is master or main
# and blocks the commit if it is. This encourages proper git workflow
# where changes are made in feature branches and merged through pull requests.

# Get the current branch name. If exit code is 0, not on any branch (detached
# HEAD state), allow the commit
BRANCH_NAME=$(git symbolic-ref --short HEAD 2>/dev/null) || exit 0

# List of protected branches
PROTECTED_BRANCHES=("master" "main")

# Check if the current branch is in the list of protected branches
for branch in "${PROTECTED_BRANCHES[@]}"; do
    if [ "$BRANCH_NAME" = "$branch" ]; then
        echo "ERROR: Direct commits to '$BRANCH_NAME' branch are not allowed."
        echo ""
        echo "Please create a feature branch and commit your changes there instead."
        echo "Then create a pull request to merge your changes into $BRANCH_NAME."
        echo ""
        echo "To create a new branch and switch to it:"
        echo "  git checkout -b feature/your-feature-name"
        echo ""
        echo "If you really need to commit directly to $BRANCH_NAME (not recommended),"
        echo "you can bypass this check with:"
        echo "  git commit --no-verify"
        echo ""
        echo "Or temporarily disable this hook:"
        echo "  git -c core.hooksPath=/dev/null commit"
        echo ""
        exit 1
    fi
done

# Not on a protected branch, allow the commit
exit 0
