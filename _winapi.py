# _winapi.py
"""
Заглушка для встроенного модуля _winapi на не-Windows платформах,
чтобы import _winapi не падал.
"""


def CopyFile2(src, dst, flags=0, progress=None):
    """
    Тесты потом перезатрут эту функцию.
    Здесь просто бросаем, чтобы модуль был валидным.
    """
    raise NotImplementedError("CopyFile2 stub on non-Windows")
