import json
from zilant_prime_core.utils.suspicion import log_suspicious_event


def test_log_suspicious_event(tmp_path, monkeypatch):
    log_file = tmp_path / "susp.log"
    from zilant_prime_core import utils

    monkeypatch.setattr(utils.suspicion, "SUSPICION_LOG", str(log_file))
    log_suspicious_event("test_event", {"foo": "bar"})
    content = log_file.read_text().strip().splitlines()[0]
    entry = json.loads(content)
    assert entry["event"] == "test_event"
    assert entry["foo"] == "bar"
    assert "time" in entry
