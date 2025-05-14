"""
Public re-exports for the container sub-package.
При таком импорте дерево функций реально исполняется,
и `pack.py` / `unpack.py` перестают висеть «мертвым грузом».
"""
from .pack import pack  # noqa: F401
from .unpack import unpack  # noqa: F401

__all__ = ["pack", "unpack"]
