# tests/conftest.py
import sys
from pathlib import Path

# <repo>/src    — кладём первым в PYTHONPATH
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
