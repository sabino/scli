from click.testing import CliRunner
from sabcli.commands.echo import echo

def test_echo():
    runner = CliRunner()
    result = runner.invoke(echo, ['Hello, World!'])
    assert result.exit_code == 0
    assert result.output.strip() == 'Hello, World!'

def test_echo_reverse():
    runner = CliRunner()
    result = runner.invoke(echo, ['Hello, World!', '--reverse'])
    assert result.exit_code == 0
    assert result.output.strip() == '!dlroW ,olleH'
