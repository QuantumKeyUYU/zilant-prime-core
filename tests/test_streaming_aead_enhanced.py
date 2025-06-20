# tests/test_streaming_aead_enhanced.py

import io
import json
import os
import pytest

import streaming_aead as sa


def test_read_exact_truncated():
    # <--- lines 102-103 in _read_exact
    with pytest.raises(EOFError, match="truncated stream"):
        sa._read_exact(io.BytesIO(b"abc"), 5)


def test_resume_decrypt_insufficient(tmp_path):
    # <--- line 118 in resume_decrypt
    f = tmp_path / "stub.bin"
    f.write_bytes(b"00")
    key = os.urandom(32)
    with pytest.raises(ValueError, match="insufficient data for resume"):
        sa.resume_decrypt(f, key, have_bytes=0, out_path=tmp_path / "out.bin")


def test_pack_and_full_unpack(tmp_path):
    # happy-path: pack_stream → resume_decrypt → unpack_stream
    data = b"hello world" * 500
    src = tmp_path / "data.bin"
    src.write_bytes(data)
    key = os.urandom(32)
    packed = tmp_path / "data.zst"
    sa.pack_stream(src, packed, key)

    # resume_decrypt should succeed if have_bytes == full size
    out1 = tmp_path / "resume.bin"
    sa.resume_decrypt(packed, key, have_bytes=packed.stat().st_size, out_path=out1)
    assert out1.read_bytes() == data

    # unpack_stream end-to-end
    out2 = tmp_path / "decode.bin"
    sa.unpack_stream(packed, out2, key)
    assert out2.read_bytes() == data


def test_unpack_stream_truncated_header(tmp_path):
    # <--- line 161 in unpack_stream
    bad = tmp_path / "bad.zst"
    bad.write_bytes(b"not a\n\ncomplete header")
    with pytest.raises(ValueError, match="truncated header"):
        sa.unpack_stream(bad, tmp_path / "o.bin", os.urandom(32))


def test_unpack_stream_mac_mismatch(tmp_path):
    # <--- line 184 in unpack_stream
    data = b"secret!"
    src = tmp_path / "in.bin"
    src.write_bytes(data)
    key = os.urandom(32)
    packed = tmp_path / "mismatch.zst"
    sa.pack_stream(src, packed, key)

    # испортим header.root_tag
    raw = packed.read_bytes()
    header, body = raw.split(b"\n\n", 1)
    meta = json.loads(header.decode())
    meta["root_tag"] = "00" * (len(bytes.fromhex(meta["root_tag"])))
    packed.write_bytes(json.dumps(meta).encode() + b"\n\n" + body)

    with pytest.raises(ValueError, match="MAC mismatch"):
        sa.unpack_stream(packed, tmp_path / "o2.bin", key)
