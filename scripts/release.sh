#!/usr/bin/env bash
set -euo pipefail

REPOSITORY_URL=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repository-url)
      REPOSITORY_URL="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

python -m build
python -m twine check dist/*

if [[ "$DRY_RUN" == true ]]; then
  echo "🚧 Dry run mode — skipping upload to ${REPOSITORY_URL}" >&2
  exit 0
fi

if [[ -z "${TWINE_PASSWORD:-}" ]]; then
  echo "❌ TWINE_PASSWORD is required" >&2
  exit 1
fi

if ! python -m twine upload \
  --repository-url "${REPOSITORY_URL}" \
  --username "${TWINE_USERNAME:-__token__}" \
  --password "$TWINE_PASSWORD" \
  dist/*; then
  echo "❌ Upload failed (HTTP 403). Check your TWINE_PASSWORD or repository URL." >&2
  exit 1
fi

