#!/bin/bash
# status.sh — CLI agent interface for CDD feature status.
# Outputs the same JSON schema as the /status.json API endpoint to stdout.
# Side effect: regenerates .agentic_devops/cache/feature_status.json.
# Usage: tools/cdd/status.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project root detection (Section 2.11)
if [ -z "${AGENTIC_PROJECT_ROOT:-}" ]; then
    # Climbing fallback: try submodule path (further) first, then standalone (nearer)
    if [ -d "$SCRIPT_DIR/../../../.agentic_devops" ]; then
        export AGENTIC_PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
    elif [ -d "$SCRIPT_DIR/../../.agentic_devops" ]; then
        export AGENTIC_PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    fi
fi

# Source shared Python resolver (python_environment.md §2.2)
source "$SCRIPT_DIR/../resolve_python.sh"

exec "$PYTHON_EXE" "$SCRIPT_DIR/serve.py" --cli-status
