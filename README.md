# sabcli

A Python CLI tool with various utilities.

## Installation

```bash
pip install git+https://github.com/sabino/scli.git
sabcli echo "Hello, World!"
sabcli echo "Hello, World!" --reverse

scli echo "Hello, World!"
scli echo "Hello, World!" --reverse
```

### Enriching Prompts

To enrich a prompt using GPT-4, use the `--enrich-prompt` (or `-ep`) option. You can also specify styles as a string using the `--style` (or `-s`) option:

```bash
sabcli generate-image --prompt "a cat" --enrich-prompt --style "artistic" --model "OfficialStableDiffusion/sd_xl_base_1.0" --width 1024 --height 1024 --output /path/to/save

### Generating Images

To generate an image using the CLI, use the following command:

```bash
sabcli generate-image --prompt "a cat" --model "OfficialStableDiffusion/sd_xl_base_1.0" --width 1024 --height 1024 --output /path/to/save
```

You can also pass dynamic arguments using the `-d` option:

```bash
sabcli generate-image --prompt "a cat" -d model OfficialStableDiffusion/sd_xl_base_1.0 -d images 1 -s "artistic" --output /path/to/save

## Running Tests

To run the tests, use the following command:

```bash
pytest

## Usage

### Running Tests

To run the tests using the CLI, use the following command:

```bash
sabcli test
```

```bash
sabcli echo "Hello, World!"
sabcli echo "Hello, World!" --reverse
```
