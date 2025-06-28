# tests/test_monitor.py (или другой подходящий файл)

import importlib
import pytest


def reload_monitor():
    # Загружаем модуль monitor.
    # Если вы используете структуру проекта, где monitor находится в src.zilant_prime_core.self_heal,
    # то импортируйте его соответствующим образом.
    import src.zilant_prime_core.self_heal.monitor as monitor_module

    importlib.reload(monitor_module)
    return monitor_module


def test_monitor_container_no_watchdog(monkeypatch):
    """
    Проверяет, что monitor_container вызывает ImportError, если watchdog недоступен.
    """
    m = reload_monitor()
    # Мокируем Observer как None, чтобы имитировать отсутствие watchdog
    monkeypatch.setattr(m, "Observer", None)

    # Проверяем, что вызов monitor_container приводит к ImportError
    with pytest.raises(ImportError) as excinfo:
        m.monitor_container("/some/path")

    assert "watchdog is required for monitor_container" in str(excinfo.value)
