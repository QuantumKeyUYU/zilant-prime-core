from __future__ import annotations

import cProfile
import io
import pstats
import threading
import time

from flask import Flask, Response, request
from prometheus_client import CONTENT_TYPE_LATEST

from .metrics import metrics

app = Flask(__name__)


@app.route("/healthz")
def healthz() -> tuple[str, int]:
    return "ok", 200


@app.route("/metrics")
def metrics_endpoint() -> Response:
    data = metrics.export()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)


@app.route("/pprof")
def pprof() -> Response:
    duration = float(request.args.get("duration", 2))
    prof = cProfile.Profile()
    prof.enable()
    time.sleep(duration)
    prof.disable()
    buf = io.StringIO()
    pstats.Stats(prof, stream=buf).sort_stats("cumulative").print_stats()
    return Response(buf.getvalue(), mimetype="text/plain")


def start_server(port: int) -> threading.Thread:
    th = threading.Thread(target=app.run, kwargs={"port": port})
    th.daemon = True
    th.start()
    return th
