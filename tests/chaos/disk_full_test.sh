#!/usr/bin/env bash
set -euo pipefail
TMPDIR=$(mktemp -d)
head -c 1048576 </dev/zero > "$TMPDIR/fill" || true
python - <<'PY'
print('disk full test completed')
PY
rm -f "$TMPDIR/fill"
rmdir "$TMPDIR"
