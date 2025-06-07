#!/usr/bin/env bash
set -euo pipefail

command -v syft >/dev/null || { echo "\u274c syft not found"; exit 1; }
command -v grype >/dev/null || { echo "\u274c grype not found"; exit 1; }

syft packages . -o cyclonedx-json=sbom.json
if grype --help 2>&1 | grep -q -- '--skip-db-update'; then
  grype sbom:sbom.json --skip-db-update --fail-on HIGH || true
else
  GRYPE_DB_AUTO_UPDATE=false grype sbom:sbom.json --fail-on HIGH || true
fi
