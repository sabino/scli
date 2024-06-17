import click
import requests
import json
import os
from openai import OpenAI
import openai
import yaml
import time
import climage


@click.command()
@click.option("--hostname", default="localhost", help="Hostname of the server")
@click.option("--port", default=7801, help="Port of the server")
@click.option("--prompt", required=True, help="Prompt for the image generation")
@click.option("--session_id", default=None, help="Existing session ID")
@click.option(
    "--model",
    default="OfficialStableDiffusion/sd3_medium_incl_clips",
    help="Model to use for image generation",
)
@click.option("--images", default=1, help="Number of images to generate")
@click.option(
    "--dynamic",
    "-d",
    multiple=True,
    type=(str, str),
    help="Dynamic arguments to be added to the JSON payload",
)
@click.option(
    "--output",
    default="./output",
    required=True,
    help="Directory to save the generated image",
)
@click.option(
    "--enrich-prompt", "-ep", is_flag=True, help="Use GPT-4 to enrich the prompt"
)
@click.option(
    "--style",
    "-s",
    type=str,
    help="YAML file with styles for enriching the prompt",
)
@click.option(
    "--climage-output",
    "-co",
    type=bool,
    default=False,
    help="Output the image using climage",
)
@click.option(
    "--open-output",
    "-o",
    type=bool,
    default=True,
    help="Open the image using the default image viewer",
)
def generate_image(
    hostname,
    port,
    prompt,
    session_id,
    model,
    images,
    dynamic,
    output,
    enrich_prompt,
    style,
    climage_output,
    open_output,
):
    """Generate an image using the specified parameters."""
    base_url = f"http://{hostname}:{port}/API"

    click.echo("🌟 Starting the magical journey of image generation...")

    # Step 1: Authentication (Session)
    try:
        if not session_id:
            click.echo(
                "🔑 Seeking permission from the wise server to start a new session..."
            )
            response = requests.post(
                f"{base_url}/GetNewSession",
                headers={"Content-Type": "application/json"},
                data=json.dumps({}),
            )
            response.raise_for_status()
            session_id = response.json().get("session_id")
            click.echo(f"✅ Session established with ID: {session_id}")
        else:
            click.echo(f"🔄 Using existing session ID: {session_id}")
    except requests.RequestException as e:
        click.echo(f"❌ Failed to establish session: {e}")
        return

    # Step 2: Enrich the prompt (if requested)
    if enrich_prompt:
        try:
            click.echo("🧠 Summoning the wisdom of GPT-4 to enrich the prompt...")
            enriched_prompt = enrich_prompt_with_gpt4(prompt, style)
            click.echo(f"✨ Enriched prompt received: {enriched_prompt}")
            prompt = enriched_prompt
        except Exception as e:
            click.echo(f"❌ Failed to enrich prompt: {e}")
            return

    # Step 3: Prepare the payload
    payload = {
        "session_id": session_id,
        "images": images,
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
    }

    if model:
        payload["model"] = model

    for key, value in dynamic:
        payload[key] = value

    click.echo("📦 Preparing the magical ingredients for image generation...")
    click.echo(f"🔍 Parameters: {json.dumps(payload, indent=2)}")

    # Step 4: Check if the image already exists
    existing_image = find_existing_image(output, prompt, model)
    if existing_image:
        click.echo(f"🖼️  Image already exists: {existing_image}")
        return

    # Step 5: Generate the image
    try:
        click.echo(
            "🎨 Casting the spell to generate the image... This might take a moment..."
        )
        response = requests.post(
            f"{base_url}/GenerateText2Image",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        response.raise_for_status()
        response_json = response.json()
        click.echo("🖼️  The image has been conjured successfully!")
    except requests.RequestException as e:
        click.echo(f"❌ Failed to generate image: {e}")
        return

    # Step 5: Save the image
    try:
        image_url = response_json.get("images", [None])[0]
        if image_url:
            click.echo("💾 Saving the enchanted image to your local repository...")
            image_response = requests.get(f"http://{hostname}:{port}/{image_url}")
            image_response.raise_for_status()
            image_path = f"{output}/{image_url.split('/')[-1]}"
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            click.echo(f"✅ Image saved to {image_path}")
            if climage_output:
                click.echo("🖼️ Displaying the image using climage...")
                output = climage.convert(image_path, is_unicode=True)
                click.echo(output)
            if open_output:
                click.echo("📎 Opening the image using the default image viewer...")
                os.system(f"open '{image_path}'")
        else:
            click.echo("❌ No image URL found in the response.")
    except requests.RequestException as e:
        click.echo(f"❌ Failed to save image: {e}")


def enrich_prompt_with_gpt4(prompt, styles):
    """Enrich the prompt using GPT-4 and styles from a YAML file."""
    client = OpenAI()

    with open(os.path.join("res", "messages.yaml"), "r") as file:
        messages = yaml.safe_load(file)["messages"]

    if styles:
        style_instructions = f"\n {styles}"
    else:
        style_instructions = "any style you want to add to the prompt."

    messages.append(
        {
            "role": "user",
            "content": f"Enrich the following prompt: '{prompt}' with the following styles: {style_instructions}",
        }
    )

    completion = client.chat.completions.create(model="gpt-4o", messages=messages)

    enriched_prompt = completion.choices[0].message.content

    return enriched_prompt


def find_existing_image(output_dir, prompt, model):
    """Check if an image with the same prompt, model, and seed already exists."""
    for filename in os.listdir(output_dir):
        if filename.endswith(".png"):
            parts = filename.split("-")
            if len(parts) > 2:
                existing_prompt = parts[1]
                existing_model = parts[2]
                existing_seed = parts[-1].split(".")[0]
                if existing_prompt == prompt and existing_model == model:
                    return os.path.join(output_dir, filename)
    return None
