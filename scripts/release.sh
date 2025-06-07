#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_URL=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --repository-url)
      REPOSITORY_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "${TWINE_PASSWORD:-}" ]]; then
  echo "❌ TWINE_PASSWORD is required" >&2
  exit 1
fi

python -m build
python -m twine check dist/*
python -m twine upload \
  --repository-url "${REPOSITORY_URL}" \
  --username "${TWINE_USERNAME:-__token__}" \
  --password "$TWINE_PASSWORD" \
  dist/*

