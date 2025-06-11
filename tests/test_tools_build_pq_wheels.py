import os
from pathlib import Path
from tools.build_pq_wheels import main


def test_build_pq_wheels_places_files(tmp_path, monkeypatch):
    pq_dir = tmp_path / "third_party" / "pqclean" / "pkg"
    pq_dir.mkdir(parents=True)
    (pq_dir / "setup.py").write_text("# dummy setup")
    dist = tmp_path / "dist"
    dist.mkdir()
    monkeypatch.setenv("PQ_DIR", str(tmp_path / "third_party" / "pqclean"))
    monkeypatch.setenv("DIST_DIR", str(dist))

    def fake_run(cmd, cwd, check):
        Path(dist / f"{Path(cwd).name}_pq.whl").write_text("")
        return None

    monkeypatch.setattr("subprocess.run", fake_run)
    main()
    files = list(dist.glob("*_pq.whl"))
    assert files, "No wheels built"
