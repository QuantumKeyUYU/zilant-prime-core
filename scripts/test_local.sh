#!/usr/bin/env bash
set -euo pipefail
# Run formatters and tests on Unix
black --check src tests
ruff check src tests
isort --check-only src tests
mypy src
export ZILANT_NO_TPM=1
pytest --maxfail=1 --disable-warnings -q
