from click.testing import CliRunner
from deployv_addon_gitlab_tools import cli


def test_main():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
