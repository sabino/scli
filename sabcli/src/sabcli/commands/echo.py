import click

@click.command()
@click.argument('text')
@click.option('-r', '--reverse', is_flag=True, help='Display the reverse of the given text')
def echo(text, reverse):
    """Echo the given text."""
    if reverse:
        text = text[::-1]
    click.echo(text)
