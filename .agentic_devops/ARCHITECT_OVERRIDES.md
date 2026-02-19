# Architect Overrides (agentic-dev-core)

> Core-specific rules for the agentic-dev-core framework repository itself.

## Sample Sync Prompt
When modifying ANY file inside `.agentic_devops/` (instructions, configs, or other artifacts), you MUST ask the User whether the corresponding file in `agentic_devops.sample/` should also be updated. Do NOT silently propagate changes to the sample folder. The sample folder is a distributable template and may intentionally diverge from the active working copy.

## Feature Scope Restriction (Core-Specific)
Feature files (`features/*.md`) in this repository define the framework's own DevOps tooling. They are distinct from consumer project features. When modifying a feature spec, verify it does not introduce consumer-project assumptions.
