Write-Host "Running lint, format, mypy, tests on Windows…"
py -m black --check src tests
py -m ruff check src tests
py -m isort --check-only src tests
py -m mypy src
$env:ZILANT_NO_TPM = "1"
py -m pytest --maxfail=1 --disable-warnings -q
