import click
import subprocess
from sabcli.commands.echo import echo
from sabcli.commands.generate_image import generate_image

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
cli.add_command(generate_image)

if __name__ == '__main__':
    cli()
