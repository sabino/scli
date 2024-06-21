# sabcli

A Python CLI tool with various utilities. This tool is a wrapper around the Stable Swarm UI (which uses Stable Diffusion). It optionally uses GPT to enrich the given prompt.

## Installation

<pre>pip install git+https://github.com/sabino/scli.git</pre>

## Usage

### Echo Command
This was added just as a starting point

```bash
scli echo "Hello, World!"
scli echo "Hello, World!" --reverse
```

### Enriching Prompts

To enrich a prompt using GPT-4, use the `--enrich-prompt` (or `-ep`) option. You can also specify styles as a string using the `--style` (or `-s`) option:

```bash
scli generate-image --prompt "a cat" --enrich-prompt --style "artistic" --model "OfficialStableDiffusion/sd_xl_base_1.0" --width 1024 --height 1024 --output /path/to/save
```

**Note:** To use the enrich prompt feature, a valid OpenAI API Token needs to be set as an environment variable `OPENAI_API_KEY`.

### Generating Images

To generate an image using the CLI, use the following command:

```bash
scli generate-image --prompt "a cat" --model "OfficialStableDiffusion/sd_xl_base_1.0" --width 1024 --height 1024 --output /path/to/save
```

You can also pass dynamic arguments using the `-d` option:

```bash
scli generate-image --prompt "a cat" -d model OfficialStableDiffusion/sd_xl_base_1.0 -d images 1 -s "artistic" --output /path/to/save
```

**Note:** The `generate-image` command requires [Stable Swarm UI](https://github.com/Stability-AI/StableSwarmUI) running. You need to set the hostname, port, etc., accordingly.

### Configuration

You can set model aliases and default values for CLI parameters in the `res/models.yaml` and `res/config.yaml` files respectively.

Example `res/models.yaml`:
```yaml
# Model aliases
sd3: OfficialStableDiffusion/sd3_medium_incl_clips
sdxl: OfficialStableDiffusion/sd_xl_base_1.0
```

Example `res/config.yaml`:
```yaml
# Default values for CLI parameters
hostname: localhost
port: 7801
model: sd3
images: 1
output: ./output
```

When passing the `--model` parameter, it will use the alias if available. When passing `-d model`, it will bypass the alias lookup and use the value directly.

## Running Tests

To run the tests, use the following command:

`pytest`

To run the tests using the CLI, use the following command:

`scli test`
