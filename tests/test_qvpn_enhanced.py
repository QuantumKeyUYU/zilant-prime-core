# tests/test_qvpn_enhanced.py

from zilant_prime_core.utils.qvpn import QVPN


def test_enable_no_stem_dependency(monkeypatch):
    # эмулируем отсутствие stem: launch_tor_with_config = None
    monkeypatch.setattr("zilant_prime_core.utils.qvpn.launch_tor_with_config", None, raising=False)
    vpn = QVPN()
    assert vpn.is_enabled() is False
    # enable/disable не должны менять флаг
    vpn.enable()
    assert vpn.is_enabled() is False
    vpn.disable()
    assert vpn.is_enabled() is False


def test_enable_handles_launch_exception(monkeypatch):
    # launch бросает ошибку — is_enabled остаётся False
    def bad_launch(config, tor_cmd=None):
        raise RuntimeError("oops")

    monkeypatch.setattr("zilant_prime_core.utils.qvpn.launch_tor_with_config", bad_launch, raising=False)

    vpn = QVPN()
    vpn.enable()
    assert vpn.is_enabled() is False


def test_enable_and_disable_happy_path(monkeypatch):
    calls = []

    class FakeProc:
        def __init__(self):
            self.terminated = False

        def terminate(self):
            self.terminated = True

    def fake_launch(config, tor_cmd=None):
        calls.append((config, tor_cmd))
        return FakeProc()

    monkeypatch.setattr("zilant_prime_core.utils.qvpn.launch_tor_with_config", fake_launch, raising=False)

    vpn = QVPN(tor_path="custom-tor")
    assert not vpn.is_enabled()
    vpn.enable()
    assert vpn.is_enabled()
    # параметры вызова совпали с ожиданием
    assert calls == [({"SocksPort": "9050"}, "custom-tor")]

    # disable → terminate и сброс флага
    proc = vpn._proc
    vpn.disable()
    assert proc.terminated
    assert not vpn.is_enabled()


def test_disable_idempotent_and_safe_on_terminate_error(monkeypatch):
    class BadProc:
        def terminate(self):
            raise Exception("fail")

    # подмешиваем proc напрямую
    vpn = QVPN()
    vpn._enabled = True
    vpn._proc = BadProc()

    # disable не должен выбрасывать
    vpn.disable()
    assert vpn.is_enabled() is False
    # повторный disable — также безопасен
    vpn.disable()
    assert vpn.is_enabled() is False
