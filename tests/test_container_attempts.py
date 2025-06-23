# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import pytest

from container import pack_file, unpack_file, get_open_attempts


def test_container_attempt_counter(tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("ok")
    key = b"k" * 32
    pack_file(src, tmp_path / "f.zil", key)
    unpack_file(tmp_path / "f.zil", tmp_path / "out.txt", key)
    assert get_open_attempts(tmp_path / "f.zil") == 1
    with pytest.raises(Exception):
        unpack_file(tmp_path / "f.zil", tmp_path / "out2.txt", b"b" * 32)
    assert get_open_attempts(tmp_path / "f.zil") == 2


