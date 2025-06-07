from zilant_prime_core.notify import Notifier


class Dummy:
    def __init__(self):
        self.sent = []

    def post(self, url, json=None, data=None, timeout=None):
        self.sent.append(url)

        class Resp:
            status_code = 200

        return Resp()


def test_notify_slack(monkeypatch):
    dummy = Dummy()
    monkeypatch.setattr("requests.post", dummy.post)
    n = Notifier()
    n.slack_url = "http://example.com"
    n.notify("oops")
    assert dummy.sent
