# How We Work: The Agentic Workflow

> **Layered Instructions:** This file is the **base layer** of the workflow philosophy, provided by the agentic-dev-core framework. Project-specific workflow additions are defined in the **override layer** at `.agentic_devops/HOW_WE_WORK_OVERRIDES.md`. At runtime, both layers are concatenated (base first, then overrides).

## 1. Core Philosophy: "Code is Disposable"
The single source of truth for any project using this framework is not the code, but the **Specifications** and **Architectural Policies** stored in the project's `features/` directory.
*   If the application code is lost, it must be reproducible from the specs.
*   We never fix bugs in code first; we fix the specification that allowed the bug.

## 2. Roles and Responsibilities

### The Architect Agent
*   **Focus:** "The What and The Why".
*   **Ownership:** Architectural Policies, Feature Specifications, instruction overrides.
*   **Key Duty:** Designing rigorous, unambiguous specifications and enforcing architectural invariants.

### The Builder Agent
*   **Focus:** "The How".
*   **Ownership:** Implementation code, tests, and the DevOps tools.
*   **Key Duty:** Translating specifications into high-quality, verified code and documenting implementation discoveries.

### The Human Executive
*   **Focus:** "The Intent and The Review".
*   **Duty:** Providing high-level goals, performing final verification (e.g., Hardware-in-the-Loop), and managing the Agentic Evolution.

## 3. The Lifecycle of a Feature
1.  **Design:** Architect creates/refines a feature file in `features/`.
2.  **Implementation:** Builder reads the feature and implementation notes, writes code/tests, and verifies locally.
3.  **Verification:** Human Executive or automated systems perform final verification.
4.  **Completion:** Builder marks the status as `[Complete]`.
5.  **Synchronization:** Architect updates documentation and generates the Software Map.

## 4. Knowledge Colocation
We do not use a global implementation log. Tribal knowledge, technical "gotchas," and lessons learned are stored directly in the `## Implementation Notes` section at the bottom of each feature file.

## 5. The Release Protocol
Releases are synchronization points where the entire project state -- Specs, Architecture, Code, and Process -- is validated and pushed to the remote repository.

### 5.1 Milestone Mutation (The "Single Release File" Rule)
We do not maintain a history of release files in the project's features directory.
1. There is exactly ONE active Release Specification file.
2. When moving to a new release, the Architect **renames** the existing release file to the new version and updates the objectives.
3. The previous release's tests are preserved as **Regression Tests** in the new file.
4. Historical release data is tracked via `PROCESS_HISTORY.md` and the project's root `README.md`.

## 6. Layered Instruction Architecture

### Overview
The agentic-dev-core framework uses a two-layer instruction model to separate framework rules from project-specific context:

*   **Base Layer** (`instructions/` directory in the framework): Contains the framework's core rules, protocols, and philosophies. These are read-only from the consumer project's perspective and are updated by pulling new versions of the framework.
*   **Override Layer** (`.agentic_devops/` directory in the consumer project): Contains project-specific customizations, domain context, and workflow additions. These are owned and maintained by the consumer project.

### How It Works
At agent launch time, the launcher scripts (`run_claude_architect.sh`, `run_claude_builder.sh`) concatenate the base and override files into a single prompt:

1. Base HOW_WE_WORK is loaded first (framework philosophy).
2. Role-specific base instructions are appended (framework rules).
3. HOW_WE_WORK overrides are appended (project workflow additions).
4. Role-specific overrides are appended (project-specific rules).

This ordering ensures that project-specific rules can refine or extend (but not silently contradict) the framework's base rules.

### Submodule Consumption Pattern
When used as a git submodule (e.g., at `agentic-dev/`):
1. The submodule provides the base layer (`agentic-dev/instructions/`) and all tools (`agentic-dev/tools/`).
2. The consumer project runs `agentic-dev/tools/bootstrap.sh` to initialize `.agentic_devops/` with override templates.
3. Tools resolve their paths via `tools_root` in `.agentic_devops/config.json`.
4. Upstream updates are pulled via `git submodule update` and audited with `agentic-dev/tools/sync_upstream.sh`.
