from click.testing import CliRunner


def test_tracing_span(tmp_path, monkeypatch):
    monkeypatch.setenv("ZILANT_TRACE", "1")
    monkeypatch.setenv("ZILANT_ALLOW_ROOT", "1")
    # metrics imported with tracing enabled via test_metrics_server
    from zilant_prime_core.cli import cli

    src = tmp_path / "f.txt"
    src.write_text("x")
    res = CliRunner().invoke(
        cli,
        ["pack", str(src), "-p", "pw", "--dry-run"],
        env={"ZILANT_TRACE": "1", "ZILANT_ALLOW_ROOT": "1"},
    )
    assert res.exit_code == 0
    assert "[Span]" in res.output
    assert "cli.command=pack" in res.output
