FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi
COPY src/ ./src/
RUN poetry build -f wheel

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
RUN python -c "import zilant_prime_core; zilant_prime_core.harden_linux()"
ENTRYPOINT ["zilant"]
