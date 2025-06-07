#!/usr/bin/env bash
set -euo pipefail

if ! command -v syft >/dev/null; then
  echo "\u2699\ufe0f Installing Syft CLI..."
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
    | sh -s -- -b /usr/local/bin v0.98.0
fi

if ! command -v grype >/dev/null; then
  echo "\u2699\ufe0f Installing Grype CLI..."
  curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh \
    | sh -s -- -b /usr/local/bin v0.70.0
fi

grype db update || echo "\u26a0\ufe0f DB update failed, proceeding..."

syft packages . -o cyclonedx-json=sbom.json
grype sbom:sbom.json --fail-on HIGH

