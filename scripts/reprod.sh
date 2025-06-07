#!/usr/bin/env bash
set -euo pipefail

command -v syft >/dev/null 2>&1 || { echo "\u274c syft not found"; exit 1; }
command -v grype >/dev/null 2>&1 || { echo "\u274c grype not found"; exit 1; }

echo "\u2699\ufe0f Updating Grype DB..."
grype db update || echo "\u26a0\ufe0f Grype DB update failed, proceeding with existing DB..."

echo "\ud83d\udce6 Generating SBOM..."
syft packages . -o cyclonedx-json=sbom.json

echo "\ud83d\udd0d Scanning SBOM for vulnerabilities..."
grype sbom:sbom.json --fail-on HIGH

