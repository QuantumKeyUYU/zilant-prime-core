from zilant_prime_core.utils.suspicion import increment_suspicion


def test_increment_suspicion(tmp_path, monkeypatch):
    home = tmp_path
    monkeypatch.setenv("HOME", str(home))
    increment_suspicion("oops")
    log = home / ".zilant" / "suspicion.log"
    assert log.exists()
    data = log.read_text()
    assert "oops" in data
