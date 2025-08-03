# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
"""
Базовый пакет **zilant_prime_core**.

* Поддержка CPython 3.8 – 3.13+.
* Ленивая загрузка подпакетов (PEP 562).
* «Горячий» патч для Hypothesis 6.99+ / Python 3.13 —
  устраняет падения во время сбора тестов.
"""

from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace
from typing import Any, Mapping, MutableMapping, Sequence

__all__: Sequence[str] = (
    "VERSION",
    "lazy_submodules",
)

VERSION = "0.7.0"  # обновите при релизе

# --------------------------------------------------------------------------- #
#                    1. Л е н и в а я   з а г р у з к а                       #
# --------------------------------------------------------------------------- #
lazy_submodules: Mapping[str, str] = {
    # «корневые» подпакеты
    "cli": ".cli",
    "cli_commands": ".cli_commands",
    "container": ".container",
    "crypto": ".crypto",
    "self_heal": ".self_heal",
    "utils": ".utils",
    "vdf": ".vdf",
    # отдельные модули
    "decoy_gen": ".decoy_gen",
    "metrics": ".metrics",
    "notify": ".notify",
    "uniform_container": ".uniform_container",
    "watchdog": ".watchdog",
    "zilfs": ".zilfs",
}


def __getattr__(name: str) -> Any:  # noqa: D401
    """
    Ленивая подгрузка подпакетов.

    >>> import zilant_prime_core as zpc
    >>> zpc.crypto  # ← импорт произойдёт здесь
    <module 'zilant_prime_core.crypto' ...>
    """
    sub = lazy_submodules.get(name)
    if sub is None:  # pragma: no cover
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(sub, __name__)
    setattr(sys.modules[__name__], name, module)
    return module


# --------------------------------------------------------------------------- #
#            2. П а т ч   д л я   H y p o t h e s i s   6 . 9 9 +            #
# --------------------------------------------------------------------------- #


def _strip_simplenamespace_modules() -> None:
    """
    В `sys.modules` могут оказаться объекты ``SimpleNamespace``
    (например, при моках). Они не хэшируемы → ломают Hypothesis.

    Меняем такие записи на полноценный ``ModuleType``.
    """
    for modname, mod in list(sys.modules.items()):
        if isinstance(mod, SimpleNamespace):
            sys.modules[modname] = ModuleType(modname)


def _patch_hypothesis() -> None:
    """
    Для CPython 3.13+ и Hypothesis ≥ 6.99:

    * ``_seen_modules`` теперь может быть ``set``.
    * ``_get_local_constants`` выполняет хэширование модулей.

    Чистим кэш и оборачиваем функцию, чтобы туда не просочились
    ``SimpleNamespace``-объекты.
    """
    try:
        import hypothesis.internal.conjecture.providers as _hp  # type: ignore
    except ModuleNotFoundError:  # Hypothesis не установлен
        return

    # 2.1. Чистим _seen_modules
    seen: MutableMapping[str, Any] | set[Any] = getattr(_hp, "_seen_modules", set())
    bad = {m for m in seen if isinstance(m, SimpleNamespace)}  # type: ignore[arg-type]

    if isinstance(seen, set):
        seen.difference_update(bad)
    else:  # list-подобный контейнер
        seen[:] = [m for m in seen if m not in bad]  # type: ignore[index]

    # 2.2. Оборачиваем _get_local_constants
    _orig_get = getattr(_hp, "_get_local_constants", None)

    if callable(_orig_get):

        def _safe_get_local_constants() -> Any:  # noqa: D401
            _strip_simplenamespace_modules()
            return _orig_get()  # type: ignore[func-returns-value]

        _hp._get_local_constants = _safe_get_local_constants  # type: ignore[assignment]


# Патч нужен только на новых версиях CPython, где SimpleNamespace стал immutable
if sys.version_info >= (3, 13):  # pragma: no cover
    _strip_simplenamespace_modules()
    _patch_hypothesis()

# --------------------------------------------------------------------------- #
#                         3. С л у ж е б н ы е   х э л п ы                    #
# --------------------------------------------------------------------------- #


def _module_constants() -> Mapping[str, Any]:  # pragma: no cover
    """Отладочная выдача внутреннего состояния пакета."""
    return {
        "VERSION": VERSION,
        "lazy_loaded": {k: v for k, v in vars(sys.modules[__name__]).items() if k in lazy_submodules},
    }


# --------------------------------------------------------------------------- #
#                                   К О Н Е Ц                                 #
# --------------------------------------------------------------------------- #
