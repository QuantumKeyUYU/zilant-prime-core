#!/usr/bin/env bash
set -euo pipefail

command -v syft >/dev/null 2>&1 || { echo "\u274c syft not found"; exit 1; }
command -v grype >/dev/null 2>&1 || { echo "\u274c grype not found"; exit 1; }

syft . -o cyclonedx-json=sbom.json
grype sbom:sbom.json --skip-db-update --fail-on HIGH
