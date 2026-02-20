# QA Overrides (agentic-dev-core)

> Core-specific rules for the agentic-dev-core framework repository itself.

## Server Startup Prohibition
You MUST NOT start DevOps tool servers (CDD Monitor, Software Map) yourself. You must instruct the User to start them and provide the exact command (e.g., `tools/cdd/start.sh`).

## Submodule Environment Verification
When verifying manual scenarios for any tool feature, always test in BOTH deployment modes:
1.  **Standalone mode:** Tools at `<project_root>/tools/`, config at `<project_root>/.agentic_devops/config.json`.
2.  **Submodule mode:** Tools at `<project_root>/<submodule>/tools/`, config at `<project_root>/.agentic_devops/config.json`.

For each scenario, verify:
*   Tool discovers the correct `config.json` (consumer project's, not the submodule's).
*   Generated artifacts (logs, PIDs, caches) are written to `.agentic_devops/runtime/` or `.agentic_devops/cache/`, NOT inside the submodule directory.
*   Tool does not crash if `config.json` is malformed -- it should fall back to defaults with a warning.

Report any submodule-specific failures as `[BUG]` with the tag "submodule-compat" in the description.
