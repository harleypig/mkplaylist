# Things To Do

## Enforce Merge Commit Messages for Changelog Generation

Implement a local workflow to ensure that merge commits into `main` or
`master` include a well-structured message suitable for changelog generation.
This avoids enforcing Conventional Commits on individual WIP commits and
focuses instead on clean release messaging.

### Goals

- Prevent direct commits to `main`/`master` (already handled by `pre-commit`)
- Allow merges into `main`, but **only with structured, readable merge messages**
- Auto-generate or assist in formatting those merge messages based on the diff or commit log
- Use only local tools — no GitHub/GitLab integration required

### Implementation Plan

1. **Create a merge helper script** (e.g., `scripts/merge-to-main.sh`) that:
    - Confirms the user is on a feature branch
    - Collects commit summaries with `git log --pretty=format:"- %s" main..HEAD`
    - Builds a merge commit message like:

      ```text
      Merge branch 'feature/something' into main

      Changes:
      - Added warp core diagnostic subroutine
      - Refactored EPS conduit mapping
      - Fixed inertial dampener calibration bug
      ```

    - Prompts the user to confirm or abort
    - Executes `git checkout main && git merge --no-ff --no-edit -m "$MERGE_MSG" feature_branch`

2. **[Optional]** Replace all manual merges with this script in team workflow

3. **[Optional]** Add `cz changelog` or similar tooling after merge to
   generate or update `CHANGELOG.md` based on commit messages

4. **Future**: Consider integrating this into a `pre-push` or `pre-merge` hook
   for enforcement

