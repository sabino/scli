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
import requests
import json
from sabcli.commands.echo import echo

@click.group()
def cli():
    pass

@click.command()
def test():
    """Run the test suite."""
    result = subprocess.run(['pytest'], capture_output=True, text=True)
    click.echo(result.stdout)

@click.command()
@click.option('--hostname', default='localhost', help='Hostname of the server')
@click.option('--port', default=7801, help='Port of the server')
@click.option('--prompt', required=True, help='Prompt for the image generation')
@click.option('--session_id', default=None, help='Existing session ID')
@click.option('--width', default=1024, help='Width of the image')
@click.option('--height', default=1024, help='Height of the image')
@click.option('--model', default=None, help='Model to use for image generation')
@click.option('--images', default=1, help='Number of images to generate')
@click.option('--dynamic', '-d', multiple=True, type=(str, str), help='Dynamic arguments to be added to the JSON payload')
def generate_image(hostname, port, prompt, session_id, width, height, model, images, dynamic):
    """Generate an image using the specified parameters."""
    base_url = f"http://{hostname}:{port}/API"
    
    if not session_id:
        response = requests.post(f"{base_url}/GetNewSession", headers={"Content-Type": "application/json"}, data=json.dumps({}))
        session_id = response.json().get("session_id")
    
    payload = {
        "session_id": session_id,
        "images": images,
        "prompt": prompt,
        "width": width,
        "height": height
    }
    
    if model:
        payload["model"] = model
    
    for key, value in dynamic:
        payload[key] = value
    
    response = requests.post(f"{base_url}/GenerateText2Image", headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    click.echo(response.json())

cli.add_command(test)
cli.add_command(echo)
cli.add_command(generate_image)

if __name__ == '__main__':
    cli()
