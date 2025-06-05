from zilant_prime_core import cli


def test_cli_exists():
    assert callable(cli.cli)
