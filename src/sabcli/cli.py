import click
from sabcli.commands.echo import echo

@click.group()
def cli():
    pass

cli.add_command(echo)

if __name__ == "__main__":
    cli()
import click
import subprocess
from sabcli.commands.echo import echo

@click.group()
def cli():
    pass

@click.command()
def test():
    """Run the test suite."""
    result = subprocess.run(['pytest'], capture_output=True, text=True)
    click.echo(result.stdout)

cli.add_command(test)
cli.add_command(echo)

if __name__ == '__main__':
    cli()
