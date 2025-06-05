#!/usr/bin/env pwsh
Write-Host "Running lint, format, mypy, tests on Windows…"
py -m black --check src tests
py -m ruff check src tests
py -m isort --check-only src tests
py -m mypy src
# Set ZILANT_SKIP_INTERACTIVE_TESTS=1 to skip CLI prompt tests
py -m pytest --maxfail=1 --disable-warnings -q
