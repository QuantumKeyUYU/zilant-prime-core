#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
import os, signal, time
pid=os.fork()
if pid==0:
    while True:
        time.sleep(1)
else:
    time.sleep(0.5)
    os.kill(pid, signal.SIGSTOP)
    time.sleep(0.5)
    os.kill(pid, signal.SIGKILL)
PY
exit 0
