# Git Worktree Guide

Git worktrees allow parallel Builder sessions to work on separate features without stepping on each other's uncommitted changes.

## Lifecycle

1. **Create** — before starting a sprint, create a worktree:
   ```bash
   git worktree add .worktrees/sprint-{N}-{feature-slug} -b sprint-{N}-{feature-slug}
   ```

2. **Build** — the Builder works exclusively in the worktree directory:
   ```bash
   cd .worktrees/sprint-{N}-{feature-slug}
   ```

3. **Evaluate** — the Evaluator checks the worktree diff:
   ```bash
   git -C .worktrees/sprint-{N}-{feature-slug} diff main
   ```

4. **Merge** — on PASS, squash merge to main:
   ```bash
   git checkout main
   git merge --squash sprint-{N}-{feature-slug}
   git commit -m "Sprint N: {feature description}"
   ```

5. **Delete** — clean up after merge:
   ```bash
   git worktree remove .worktrees/sprint-{N}-{feature-slug}
   git branch -d sprint-{N}-{feature-slug}
   ```

## Naming convention

Worktrees follow the pattern: `sprint-{N}-{feature-slug}`

- `N` = sprint number (matches the sprint contract)
- `feature-slug` = kebab-case summary of the feature

Examples:
- `sprint-1-auth-flow`
- `sprint-2-dashboard-api`
- `sprint-3-notification-service`

## How the Evaluator identifies the worktree

The sprint contract includes a `worktree` field specifying which worktree to inspect. The Evaluator reads the contract and navigates to that worktree before running verification steps.

## Branch merge strategy

- **Squash merge** is recommended to keep main's history clean
- Commit message format: `Sprint N: {feature description}`
- Delete the worktree branch after merge to keep the branch list tidy

## Directory layout

```
project-root/
├── .worktrees/              ← gitignored
│   ├── sprint-1-auth-flow/
│   └── sprint-2-dashboard/
├── src/
├── tests/
└── ...
```
