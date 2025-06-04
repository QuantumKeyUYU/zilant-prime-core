#!/usr/bin/env bash
set -e
umask 027
chmod 600 config.yaml sbom.json
chmod 600 grype-report.json trivy-report.json semgrep-report.sarif
