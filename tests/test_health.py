from zilant_prime_core.health import app


def test_health_endpoints():
    client = app.test_client()
    assert client.get("/healthz").status_code == 200
    assert client.get("/metrics").status_code == 200
