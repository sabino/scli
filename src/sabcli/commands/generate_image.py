import click
import requests
import json
import os
from openai import OpenAI
import openai
import yaml

@click.command()
@click.option('--hostname', default='localhost', help='Hostname of the server')
@click.option('--port', default=7801, help='Port of the server')
@click.option('--prompt', required=True, help='Prompt for the image generation')
@click.option('--session_id', default=None, help='Existing session ID')
@click.option('--model', default='OfficialStableDiffusion/sd3_medium_incl_clips', help='Model to use for image generation')
@click.option('--images', default=1, help='Number of images to generate')
@click.option('--dynamic', '-d', multiple=True, type=(str, str), help='Dynamic arguments to be added to the JSON payload')
@click.option('--output', default='./output', required=True, help='Directory to save the generated image')
@click.option('--enrich-prompt', '-ep', is_flag=True, help='Use GPT-4 to enrich the prompt')
@click.option('--style', '-s', type=click.Path(exists=True), help='YAML file with styles for enriching the prompt')
@click.option('--enrich-prompt', '-ep', is_flag=True, help='Use GPT-4 to enrich the prompt')
@click.option('--style', '-s', type=click.Path(exists=True), help='YAML file with styles for enriching the prompt')
def generate_image(hostname, port, prompt, session_id, model, images, dynamic, output, enrich_prompt, style):
    """Generate an image using the specified parameters."""
    base_url = f"http://{hostname}:{port}/API"
    
    if not session_id:
        response = requests.post(f"{base_url}/GetNewSession", headers={"Content-Type": "application/json"}, data=json.dumps({}))
        session_id = response.json().get("session_id")
    
    if enrich_prompt:
        enriched_prompt = enrich_prompt_with_gpt4(prompt, style)
        prompt = enriched_prompt

    if enrich_prompt:
        enriched_prompt = enrich_prompt_with_gpt4(prompt, style)
        prompt = enriched_prompt

    payload = {
        "session_id": session_id,
        "images": images,
        "prompt": prompt,
        "width": 1024,
        "height": 1024
    }
    
    if model:
        payload["model"] = model
    
    for key, value in dynamic:
        payload[key] = value
    
    response = requests.post(f"{base_url}/GenerateText2Image", headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    response_json = response.json()
    click.echo(response_json)
    
    image_url = response_json.get("images", [None])[0]
    if image_url:
        image_response = requests.get(f"http://{hostname}:{port}/{image_url}")
        image_path = f"{output}/{image_url.split('/')[-1]}"
        with open(image_path, 'wb') as f:
            f.write(image_response.content)
        click.echo(f"Image saved to {image_path}")


def enrich_prompt_with_gpt4(prompt, style_path):
    """Enrich the prompt using GPT-4 and styles from a YAML file."""
    client = OpenAI()

    with open(os.path.join('res', 'messages.yaml'), 'r') as file:
        messages = yaml.safe_load(file)['messages']

    if style_path:
        with open(os.path.join('res', style_path), 'r') as file:
            styles = yaml.safe_load(file)
        style_instructions = "\n".join(styles.get('styles', []))
    else:
        style_instructions = ""

    messages.append({"role": "user", "content": f"Enrich the following prompt: '{prompt}' with the following styles: {style_instructions}"})

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    enriched_prompt = completion.choices[0].message['content'].strip()

    return enriched_prompt
