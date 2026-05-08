# Sandbox Environment

This project supports isolated agent sessions for Builder and Evaluator agents. The isolation tier depends on the project platform.

## When to use the sandbox

- Multi-agent sessions (parallel Builders)
- Untrusted code review
- Any session where you want filesystem/network isolation

## Detecting sandbox mode

Agents can check the `HARNESS_SANDBOX` environment variable:
- If set to `true`, the agent is running inside the sandbox
- If not set, the agent is running directly on the host

## Worktree integration

Each sprint/feature gets its own git worktree so parallel Builders don't stomp each other:

```bash
# Create a worktree for sprint N
git worktree add .worktrees/sprint-N-slug -b sprint-N-slug

# List active worktrees
git worktree list

# Remove a worktree after merge
git worktree remove .worktrees/sprint-N-slug
```

The `.worktrees/` directory is at the project root and should be added to `.gitignore`.

## Docker isolation (full tier)

Each agent session runs inside a Docker container with restricted filesystem, network, and resource access. The `docker-compose.sandbox.yml` at the project root defines the builder and evaluator services.

### Starting the sandbox

```bash
# Start the Builder container
docker compose -f docker-compose.sandbox.yml up -d builder

# Start the Evaluator container
docker compose -f docker-compose.sandbox.yml up -d evaluator

# Attach to the Builder
docker compose -f docker-compose.sandbox.yml exec builder bash
```

### What is isolated

- **Filesystem**: project directory mounted read-only; only designated directories are writable (varies by platform profile)
- **Network**: internal bridge network only; a separate `registry` network allows package downloads
- **Resources**: CPU, memory, and PID limits are capped per container (varies by platform profile)
- **Host access**: no macOS Keychain, no host network, no Docker socket

### Teardown

```bash
# Stop all sandbox containers
docker compose -f docker-compose.sandbox.yml down

# Remove worktree branches after merge
git worktree prune
```
