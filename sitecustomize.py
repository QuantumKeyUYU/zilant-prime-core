# sitecustomize.py
# Подменяем pathlib.WindowsPath на PosixPath на non-Windows платформах,
# чтобы любые 'C:\\foo\\bar' не валили тесты в CI.
import pathlib
import sys

if sys.platform != "win32":  # работаем только на Linux/Mac
    pathlib.WindowsPath = pathlib.PosixPath  # type: ignore[attr-defined]
