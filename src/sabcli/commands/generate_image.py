import click
import requests
import json
import os
import openai
import yaml
import time
import climage
import base64


def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


config = load_yaml("res/config.yaml")
messages_config = load_yaml("res/messages.yaml")


@click.command()
@click.option("--hostname", default=config["hostname"], help="Hostname of the server")
@click.option("--port", default=config["port"], help="Port of the server")
@click.option("--prompt", "-p", required=True, help="Prompt for the image generation")
@click.option("--session_id", default=None, help="Existing session ID")
@click.option(
    "--model", default=config["model"], help="Model to use for image generation"
)
@click.option("--images", default=config["images"], help="Number of images to generate")
@click.option(
    "--dynamic",
    "-d",
    multiple=True,
    type=(str, str),
    help="Dynamic arguments to be added to the JSON payload",
)
@click.option(
    "--output",
    default=config["output"],
    required=True,
    help="Directory to save the generated image",
)
@click.option(
    "--enrich-prompt",
    "-ep",
    is_flag=True,
    default=config["enrich_prompt"],
    help="Use GPT-4 to enrich the prompt",
)
@click.option(
    "--style",
    "-s",
    type=str,
    default=config["style"],
    help="YAML file with styles for enriching the prompt",
)
@click.option(
    "--climage-output",
    "-co",
    type=bool,
    default=config["climage_output"],
    help="Output the image using climage",
)
@click.option(
    "--open-output",
    "-o",
    type=bool,
    default=config["open_output"],
    help="Open the image using the default image viewer",
)
@click.option(
    "--output-analysis",
    "-oa",
    is_flag=True,
    help="Use GPT-4o Vision to analyze the output image",
)
@click.option(
    "--analysis-iterations",
    "-ai",
    default=1,
    type=int,
    help="Number of times to analyze and improve the image",
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
    output_analysis,
    analysis_iterations,
):
    """Generate an image using the specified parameters."""
    base_url = f"http://{hostname}:{port}/API"

    click.echo("🌟 Starting the magical journey of image generation...")

    session_id = authenticate_session(base_url, session_id)
    if not session_id:
        return

    if enrich_prompt:
        prompt = enrich_prompt_with_gpt4(prompt, style)

    # Load model aliases
    model_aliases = load_yaml("res/models.yaml")

    # Use alias if available
    if model in model_aliases:
        model = model_aliases[model]

    payload = prepare_payload(session_id, images, prompt, model, dynamic)

    existing_image = find_existing_image(output, prompt, model)
    if existing_image:
        click.echo(f"🖼️  Image already exists: {existing_image}")
        return

    response_json = generate_image_request(base_url, payload)
    if not response_json:
        return

    save_image(response_json, hostname, port, output, climage_output, open_output)

    if output_analysis:
        for _ in range(analysis_iterations):
            click.echo("🔍 Analyzing the output image using GPT-4o Vision...")
            enriched_prompt = analyze_image_with_gpt4o_vision(output, prompt)
            payload = prepare_payload(
                session_id, images, enriched_prompt, model, dynamic
            )
            response_json = generate_image_request(base_url, payload)
            if not response_json:
                return
            save_image(
                response_json, hostname, port, output, climage_output, open_output
            )


def analyze_image_with_gpt4o_vision(output_dir, prompt):
    """Analyze the output image using GPT-4o Vision and return an enriched prompt."""
    client = openai

    # Get the latest image
    image_path = os.path.join(output_dir, os.listdir(output_dir)[-1])

    # Check if the image is below 20 MB
    if os.path.getsize(image_path) > 20 * 1024 * 1024:
        raise ValueError("Image size exceeds 20 MB")

    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Display the image path
    click.echo(f"🖼️  Analyzing the image: {image_path}")
    
    # Verify the image format
    if not image_path.lower().endswith((".png", ".jpeg", ".jpg", ".gif", ".webp")):
        raise ValueError("Unsupported image format")

    # Encode the image to base64
    encoded_image = base64.b64encode(image_data).decode("utf-8")

    messages = messages_config["analysis-instructions"]
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Analyze the following image and provide suggestions to improve it based on the prompt: '{prompt}'",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
                },
            ],
        }
    )

    completion = client.chat.completions.create(
        model="gpt-4o", messages=messages, max_tokens=300
    )

    enriched_prompt = completion.choices[0].message.content

    return enriched_prompt


def enrich_prompt_with_gpt4(prompt, styles):
    """Enrich the prompt using GPT-4 and styles from a YAML file."""
    client = openai

    messages = messages_config["generate-instructions"]

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


def authenticate_session(base_url, session_id):
    """Authenticate session with the server."""
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
        return session_id
    except requests.RequestException as e:
        click.echo(f"❌ Failed to establish session: {e}")
        return None


def prepare_payload(session_id, images, prompt, model, dynamic):
    """Prepare the payload for the image generation request."""
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

    return payload


def generate_image_request(base_url, payload):
    """Send the image generation request to the server."""
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
        return response_json
    except requests.RequestException as e:
        click.echo(f"❌ Failed to generate image: {e}")
        return None


def save_image(response_json, hostname, port, output, climage_output, open_output):
    """Save the generated image to the local repository."""
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
                os.system(f'open "{image_path}"')
        else:
            click.echo("❌ No image URL found in the response.")
    except requests.RequestException as e:
        click.echo(f"❌ Failed to save image: {e}")


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
