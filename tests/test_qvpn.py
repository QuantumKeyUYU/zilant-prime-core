# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from zilant_prime_core.utils.qvpn import QVPN
import pytest


@pytest.fixture
def mock_launch_tor(monkeypatch):
    calls = []

    def fake_launch(config, tor_cmd="tor"):
        calls.append(config)
        class P:
            def terminate(self):
                pass
        return P()

    monkeypatch.setattr("zilant_prime_core.utils.qvpn.launch_tor_with_config", fake_launch)
    return calls


def test_qvpn_toggle(mock_launch_tor):
    q = QVPN()
    assert q.is_enabled() is False
    q.enable()
    assert q.is_enabled() is True
    q.disable()
    assert q.is_enabled() is False
