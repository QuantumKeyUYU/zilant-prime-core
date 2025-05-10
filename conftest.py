# conftest.py
import os
import sys

# Добавляем папку src в sys.path, чтобы "import src.*" работал сразу
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
