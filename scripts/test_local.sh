#!/usr/bin/env bash
set -euo pipefail
# Run formatters and tests on Unix
black --check src tests
ruff check src tests
isort --check-only src tests
mypy src
export ZILANT_NO_TPM=1
# Set ZILANT_SKIP_INTERACTIVE_TESTS=1 to skip CLI prompt tests
pytest --maxfail=1 --disable-warnings -q
