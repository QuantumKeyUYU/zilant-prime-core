.PHONY: test lint fmt pq-wheels

test:
ZILANT_ALLOW_ROOT=1 pytest -q

lint:
ruff check src tests

fmt:
black src tests

pq-wheels:
python tools/build_pq_wheels.py
