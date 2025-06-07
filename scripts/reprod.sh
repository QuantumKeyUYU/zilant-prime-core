#!/usr/bin/env bash
set -euo pipefail

command -v syft >/dev/null 2>&1 || { echo "\u274c syft not found"; exit 1; }
command -v grype >/dev/null 2>&1 || { echo "\u274c grype not found"; exit 1; }

grype db update || echo "\u26a0\ufe0f DB update failed, proceeding..."

syft packages . -o cyclonedx-json=sbom.json
grype sbom:sbom.json --fail-on HIGH

