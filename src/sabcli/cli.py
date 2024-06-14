import click
from sabcli.commands.echo import echo

@click.group()
def cli():
    pass

cli.add_command(echo)

if __name__ == "__main__":
    cli()
