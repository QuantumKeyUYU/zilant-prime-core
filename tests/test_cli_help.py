# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import re
from click.testing import CliRunner

from zilant_prime_core.cli import cli


def test_cli_help_shows_usage_and_hsm_commands():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert re.search(r"hsm\s+init", result.output)
    assert re.search(r"hsm\s+seal", result.output)
    assert re.search(r"hsm\s+unseal", result.output)
    assert re.search(r"hsm\s+status", result.output)
