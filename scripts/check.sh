#!/usr/bin/env bash
# Runs every repository check. Used by GitHub Actions and the Claude Code Stop hook.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests
node --check app.js
