#!/usr/bin/env bash
set -e
syft . -o cyclonedx-json=sbom.json
grype sbom:sbom.json --fail-on HIGH
