# Feature: CDD Status Monitor

> Label: "Tool: CDD Monitor"
> Category: "DevOps Tools"


## 1. Overview
The Continuous Design-Driven (CDD) Monitor tracks the status of all feature files in `features/`. Provides both a web dashboard for human review and a canonical JSON output for agent consumption.

## 2. Requirements

### 2.1 Feature Scanning
*   **Path Awareness:** The monitor must scan the project's `features/` directory for all feature files.
*   **Status Detection:** Status is derived from a combination of file modification timestamps (for [TODO] detection) and source control history/tags.

### 2.2 UI & Layout
*   **Table Layout:** Each status section (TODO, TESTING, COMPLETE) MUST render features in a table with the following columns:
    *   **Feature** -- The feature filename.
    *   **Tests** -- The test status badge (PASS, FAIL, or blank if no `tests.json` exists).
    *   **QA** -- The QA status badge (CLEAN in green, HAS_OPEN_ITEMS in orange, or blank if no `critic.json` exists).
*   **Compact Design:** Minimal padding and margins to ensure the dashboard fits in a small window.
*   **COMPLETE Table Capping:** The "COMPLETE" section should be limited to the most recent items.
*   **Status Indicators:** Use distinct color coding for TODO, TESTING, and COMPLETE section headers.
*   **Badge Colors:** PASS/CLEAN = green, WARN/HAS_OPEN_ITEMS = orange, FAIL = red. Blank cells when no data exists (no badge, no "UNKNOWN" text).
*   **Scope:** The web dashboard is for human consumption only. Agents must use the `/status.json` API endpoint.

### 2.3 Verification Signals
*   **Test Status (Per-Feature Protocol):**
    *   The monitor resolves `tests/` relative to `PROJECT_ROOT`.
    *   For each feature `features/<name>.md`, the monitor looks up `tests/<name>/tests.json`.
    *   Only the `"status"` field is evaluated; other fields are metadata.
    *   **Per-Feature Display:** Each feature entry shows its own test status (`PASS`, `FAIL`, `UNKNOWN`). If no `tests/<name>/tests.json` exists, the `test_status` key is omitted from that entry.
    *   **Aggregation:** The top-level `test_status` aggregates all per-feature results. If ANY feature reports `FAIL`, the aggregate is **FAIL**. Only **PASS** if all features with test files report success. **UNKNOWN** if no test files exist.

### 2.4 Machine-Readable Output (Agent Interface)
*   **API Endpoint:** The server MUST expose a `/status.json` route that returns the feature status JSON directly with `Content-Type: application/json`. This is the **primary** agent interface.
*   **Canonical File:** The monitor MUST also produce a `feature_status.json` file at `tools/cdd/feature_status.json` as a secondary artifact, regenerated on every request.
*   **Schema:** Both the API response and the file MUST contain the following structure:
    ```json
    {
      "generated_at": "<ISO 8601 timestamp>",
      "test_status": "PASS | FAIL | UNKNOWN",
      "features": {
        "todo": [{"file": "<relative path>", "label": "<label>", "test_status": "PASS | FAIL | UNKNOWN"}],
        "testing": [{"file": "<relative path>", "label": "<label>"}],
        "complete": [{"file": "<relative path>", "label": "<label>", "test_status": "PASS"}]
      }
    }
    ```
    Note: The `test_status` key on individual feature entries is present only when `tests/<feature_name>/tests.json` exists.
*   **Regeneration:** The JSON MUST be freshly computed on every `/status.json` request. The file on disk is also regenerated on dashboard and API requests.
*   **Deterministic Output:** Arrays MUST be sorted by file path. Keys MUST be sorted.
*   **Agent Contract:** Agents MUST query status via `curl http://localhost:<port>/status.json` where `<port>` is read from `.agentic_devops/config.json` (`cdd_port`, default `8086`). Agents MUST NOT scrape the web dashboard or guess ports.

### 2.5 QA Status Integration
*   **Critic JSON Discovery:** For each feature `features/<name>.md`, the monitor checks for `tests/<name>/critic.json` on disk.
*   **Per-Feature QA Status:** If `critic.json` exists, the monitor reads the `user_testing.status` field and exposes it as `qa_status` on the feature entry (`CLEAN` or `HAS_OPEN_ITEMS`). If no `critic.json` exists, the `qa_status` key is omitted.
*   **No Top-Level Aggregation:** There is no top-level `critic_status` or `qa_status` field. QA status is per-feature only.
*   **Dashboard Column:** Each feature entry on the web dashboard displays a QA column showing `CLEAN` (green) or `HAS_OPEN_ITEMS` (orange). Blank when no `critic.json` exists.
*   **No Blocking:** The `critic_gate_blocking` config key is deprecated (no-op). CDD does not gate status transitions based on critic or QA results.

## 3. Scenarios

### Automated Scenarios
These scenarios are validated by the Builder's automated test suite.

#### Scenario: Agent Reads Feature Status via API
    Given the CDD server is running
    When an agent needs to check feature queue status
    Then the agent reads cdd_port from .agentic_devops/config.json
    And the agent calls GET /status.json on that port
    And the agent receives a valid JSON response
    And the agent does NOT scrape the web dashboard or guess ports

#### Scenario: Zero-Queue Verification
    Given a release is being prepared
    When the Architect checks the Zero-Queue Mandate
    Then the Architect calls GET /status.json on the configured CDD port
    And verifies that the "todo" and "testing" arrays are empty

#### Scenario: QA Status in API Response
    Given the CDD server is running
    And tests/<feature_name>/critic.json exists with user_testing.status CLEAN
    When an agent calls GET /status.json
    Then the feature entry includes a qa_status field with value CLEAN
    And the top-level response does NOT include a critic_status field

#### Scenario: QA Status Omitted When No Critic File
    Given the CDD server is running
    And no critic.json exists for a feature
    When an agent calls GET /status.json
    Then the feature entry does not include a qa_status field

### Manual Scenarios (Human Verification Required)
These scenarios MUST NOT be validated through automated tests. The Builder must start the server and instruct the User to verify the web dashboard visually.

#### Scenario: Web Dashboard Display
    Given the CDD server is running
    When the User opens the web dashboard in a browser
    Then each status section (TODO, TESTING, COMPLETE) displays features in a table
    And the table has columns for Feature, Tests, and QA
    And test badges show PASS/FAIL with appropriate colors
    And QA badges show CLEAN (green) or HAS_OPEN_ITEMS (orange)
    And cells are blank when no tests.json or critic.json exists for that feature

#### Scenario: Web Dashboard Auto-Refresh
    Given the User is viewing the web dashboard
    When a feature status changes (e.g., a status commit is made)
    Then the dashboard reflects the updated status within 5 seconds

#### Scenario: QA Column on Dashboard
    Given the CDD server is running
    And critic.json files exist for some features
    When the User opens the web dashboard
    Then each feature with a critic.json shows CLEAN or HAS_OPEN_ITEMS in the QA column
    And features without critic.json show a blank QA cell

## 4. Implementation Notes
*   **Test Scope:** Automated tests MUST only cover the `/status.json` API endpoint and the underlying status logic. The web dashboard HTML rendering and visual layout MUST NOT be tested through automated tests. The Builder MUST NOT start the CDD server. After passing automated tests, the Builder should use the `[Ready for Verification]` status tag and instruct the User to start the server (`tools/cdd/start.sh`) and visually verify the dashboard.
*   **Visual Polish:** Use a dark, high-contrast theme suitable for 24/7 monitoring.
*   **Test Isolation:** The test aggregator scans `tests/<feature_name>/tests.json` (resolved relative to `PROJECT_ROOT`) and treats malformed JSON as FAIL.
*   **Name Convention:** Feature-to-test mapping uses the feature file's stem: `features/<name>.md` maps to `tests/<name>/tests.json`. The `<name>` must match exactly (case-sensitive).
*   **Server-Side Rendering:** The HTML is generated dynamically per request (no static `index.html`). Auto-refreshes every 5 seconds via `<meta http-equiv="refresh">`.
*   **Status Logic:** `COMPLETE` requires `complete_ts > test_ts` AND `file_mod_ts <= complete_ts`. Any file edit after the completion commit resets status to `TODO` (the "Status Reset" protocol).
*   **Escape Sequences:** Git grep patterns use `\\[` / `\\]` in f-strings to avoid Python 3.12+ deprecation warnings for invalid escape sequences.
*   **Agent Interface:** The `/status.json` API endpoint is the primary machine-readable contract. All agent tooling (Status Management, Context Clear Protocol, Release Protocol Zero-Queue checks) MUST use `curl http://localhost:<cdd_port>/status.json`. The disk file `feature_status.json` is a secondary artifact. Agents MUST read the port from `.agentic_devops/config.json` (`cdd_port` key, default `8086`) and MUST NOT hardcode or guess port numbers.
*   **Path Normalization:** `os.path.relpath` may resolve to `.`, making `features_rel` = `./features`. The `f_path` used for git grep MUST be normalized with `os.path.normpath()` to strip the `./` prefix, otherwise status commit patterns like `[Complete features/file.md]` won't match `./features/file.md`.
