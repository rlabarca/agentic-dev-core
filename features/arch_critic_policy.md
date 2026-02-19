# Architectural Policy: Critic Quality Gate

> Label: "Policy: Critic Quality Gate"
> Category: "Quality Assurance"

## 1. Purpose
This policy defines the invariants and constraints governing the Critic Quality Gate system -- the automated and semi-automated verification layer that ensures specification-implementation alignment across the framework.

## 2. Invariants

### 2.1 Dual-Gate Principle
Every feature MUST be evaluable through two independent gates:

*   **Spec Gate (Pre-Implementation):** Validates that the feature specification itself is structurally complete, properly anchored to architectural policies, and contains well-formed Gherkin scenarios. This gate can run before any code exists.
*   **Implementation Gate (Post-Implementation):** Validates that the implementation aligns with the specification through traceability checks, policy adherence, builder decision audit, and (optionally) LLM-based logic drift detection.

Neither gate alone is sufficient. A feature that passes the Spec Gate but fails the Implementation Gate has a code problem. A feature that passes the Implementation Gate but fails the Spec Gate has a specification problem.

### 2.2 Traceability Mandate
Every automated Gherkin scenario in a feature file MUST be traceable to at least one automated test function. Traceability is established through keyword matching between scenario titles and test function names/bodies.

*   The traceability engine uses a keyword extraction and matching approach (2+ keyword threshold).
*   Manual scenarios are EXEMPT from traceability but are flagged if automated tests exist for them.
*   Explicit `traceability_overrides` in Implementation Notes allow manual mapping when keyword matching is insufficient.

### 2.3 Builder Decision Transparency
The Builder MUST classify every non-trivial implementation decision using structured tags in the `## Implementation Notes` section:

| Tag | Severity | Meaning |
|-----|----------|---------|
| `[CLARIFICATION]` | INFO | Interpreted ambiguous spec language. The spec was unclear; Builder chose a reasonable interpretation. |
| `[AUTONOMOUS]` | WARN | Spec was silent on this topic. Builder made a judgment call to fill the gap. |
| `[DEVIATION]` | HIGH | Intentionally diverged from what the spec says. Requires Architect acknowledgment. |
| `[DISCOVERY]` | HIGH | Found an unstated requirement during implementation. Requires Architect acknowledgment. |

**Constraint:** A feature with unacknowledged `[DEVIATION]` or `[DISCOVERY]` entries MUST NOT transition to `[Complete]` when `critic_gate_blocking` is enabled.

### 2.4 User Testing Feedback Loop
The QA Agent records findings during manual verification using three discovery types:

| Type | Meaning |
|------|---------|
| `[BUG]` | Behavior contradicts an existing scenario. |
| `[DISCOVERY]` | Behavior exists but no scenario covers it. |
| `[INTENT_DRIFT]` | Behavior matches the spec literally but misses the actual intent. |

**Constraint:** Discoveries follow a lifecycle: `OPEN -> SPEC_UPDATED -> RESOLVED -> PRUNED`. A feature with OPEN discoveries MUST NOT transition to `[Complete]` when `critic_gate_blocking` is enabled.

### 2.5 Policy Adherence
Architectural policy files (`arch_*.md`) MAY define `FORBIDDEN:` patterns -- literal strings or regex patterns that MUST NOT appear in the implementation code of features anchored to that policy.

*   The Critic tool scans implementation files for FORBIDDEN pattern violations.
*   Any violation produces a FAIL on the Implementation Gate.

## 3. Configuration

The following keys in `.agentic_devops/config.json` govern Critic behavior:

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `critic_llm_model` | string | `claude-sonnet-4-20250514` | Model used for logic drift detection. |
| `critic_llm_enabled` | boolean | `false` | Whether the LLM-based logic drift engine is active. |
| `critic_gate_blocking` | boolean | `false` | Whether Critic FAIL/WARN blocks status transitions. |

## 4. Output Contract
The Critic tool MUST produce:

*   **Per-feature:** `tests/<feature_name>/critic.json` with `spec_gate`, `implementation_gate`, and `user_testing` sections.
*   **Aggregate:** `CRITIC_REPORT.md` at the project root summarizing all features.

## Implementation Notes
*   This policy governs buildable tooling constraints (the Critic tool itself), not process rules. It is valid under the Feature Scope Restriction mandate.
*   The `critic_gate_blocking` flag defaults to `false` to allow gradual adoption. Teams can enable it once their specs reach sufficient maturity.
*   FORBIDDEN patterns are optional. Not all architectural policies need to define them.
