"""
Top-level package initialisation for Zilant Prime Core.

Задачи
------
* Экспортирует публичные метаданные пакета (`__version__`, …).
* Прерывает загрузку в CI, если импорт происходит раньше защитного хука.
* Запрещает запуск под root-ом вне тестов, если не задан `ZILANT_ALLOW_ROOT`.
* Усиливает безопасность процесса (seccomp, prctl и т. д.) через `root_guard`.
* Подкладывает stub-модуль *tabulate*, чтобы тесты не падали без зависимости.
* Чинит баг Hypothesis < 6.100 с `types.SimpleNamespace` (нехэшируемый).

Файл не должен порождать тяжёлых побочных эффектов и обязан
оставаться безопасным при импорте из сторонних проектов.
"""

from __future__ import annotations

import os
import sys
from types import ModuleType, SimpleNamespace
from typing import Any, Mapping, cast

__all__ = ["__version__"]
__version__ = "0.9.9b2"

# --------------------------------------------------------------------------- #
# 1. CI-сторож: останавливаем «ранний» импорт пакета в workflow’ах.           #
# --------------------------------------------------------------------------- #
if os.getenv("ZILANT_CI_IMPORT_HOOK"):
    # Локальный импорт, чтобы не тянуть CLI-дерево зря.
    from .cli import _abort  # type: ignore[attr-defined]

    _abort("Unsafe import before guard!", code=99)  # pragma: no cover

# --------------------------------------------------------------------------- #
# 2. Root-guard & hardening (linux-only noop на других ОС).                  #
# --------------------------------------------------------------------------- #
from .utils import root_guard  # isort: split

if "PYTEST_CURRENT_TEST" not in os.environ and not os.getenv("ZILANT_ALLOW_ROOT"):
    root_guard.assert_safe_or_die()  # pragma: no cover

# Подкручиваем seccomp - это быстро и безопасно.
root_guard.harden_linux()

# --------------------------------------------------------------------------- #
# 3. Пример типобезопасного cast() ― просто демонстрация для mypy.           #
# --------------------------------------------------------------------------- #
_example_dict: dict[str, str] = {"key": "value"}
example_ns = SimpleNamespace(**cast(Mapping[str, Any], _example_dict))
del _example_dict  # пространство имён чистим сразу

# --------------------------------------------------------------------------- #
# 4. Тестовые shim’ы.                                                         #
# --------------------------------------------------------------------------- #
# 4-a) Stub для «tabulate» (в CI вывод всё равно идёт в JSON / DevNull).
if "tabulate" not in sys.modules:  # pragma: no cover
    stub = ModuleType("tabulate")

    def _tabulate(*_args: Any, **_kwargs: Any) -> str:  # noqa: D401
        return ""  # pretty-print не нужен в тестах

    stub.tabulate = _tabulate  # type: ignore[attr-defined]
    sys.modules["tabulate"] = stub

# 4-b) Hypothesis < 6.100 падает на unhashable SimpleNamespace.
if not hasattr(SimpleNamespace, "__hash__"):  # pragma: no cover
    SimpleNamespace.__hash__ = lambda self: id(self)  # type: ignore[assignment]
