from click.testing import CliRunner

from ubiops_cli.main import cli
from ubiops_cli.version import VERSION


def test_help():
    """CLI --help exits cleanly and shows the description."""
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "UbiOps command line interface" in result.output


def test_version():
    """CLI --version prints the current version."""
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert VERSION in result.output
