import os
from pathlib import Path
from tools.gen_threat_diagram import main


def test_gen_threat_diagram_creates_file(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "foo.py").write_text("class ExampleThreatModel:\n    pass\n")
    out_dir = tmp_path / "docs"
    out_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    os.environ["ZILANT_ALLOW_ROOT"] = "1"
    out_path = out_dir / "threats.mmd"
    main(str(src), str(out_path))
    content = out_path.read_text()
    assert "ExampleThreatModel" in content
