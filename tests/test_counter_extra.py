from pathlib import Path

from zilant_prime_core.utils.counter import Counter


def test_counter_file_init_and_increment(tmp_path):
    f = tmp_path / "count.txt"
    f.write_text("5")
    c = Counter(f)
    assert c.value == 5
    c.increment()
    assert f.read_text() == "6"
    assert c.value == 6


def test_counter_invalid_file(tmp_path):
    f = tmp_path / "count.txt"
    f.write_text("oops")
    c = Counter(f)
    assert c.value == 0
    c.increment()
    assert f.read_text() == "1"


def test_counter_write_error(tmp_path, monkeypatch):
    f = tmp_path / "count.txt"
    c = Counter(f)
    orig_write = Path.write_text

    def fail(self, data):
        if self == f:
            raise OSError("boom")
        return orig_write(self, data)

    monkeypatch.setattr(Path, "write_text", fail)
    assert c.increment() == 1
    assert not f.exists()
