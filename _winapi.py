# _winapi.py
# stub-модуль для Linux/CI, чтобы import _winapi не падал в тестах

def CopyFile2(src, dst, flags=0, progress=None):
    """
    Заглушка Windows CopyFile2 — на *nix её не вызывают.
    При случайном вызове выбрасывает OSError.
    """
    raise OSError("CopyFile2 is not supported on this platform")
