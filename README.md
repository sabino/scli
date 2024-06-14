# sabcli

A Python CLI tool with various utilities.

## Installation

```bash
pip install .
sabcli echo "Hello, World!"
sabcli echo "Hello, World!" --reverse

scli echo "Hello, World!"
scli echo "Hello, World!" --reverse
```

### Generating Images

To generate an image using the CLI, use the following command:

```bash
sabcli generate-image --prompt "a cat" --model "OfficialStableDiffusion/sd_xl_base_1.0" --width 1024 --height 1024 --output /path/to/save
```

You can also pass dynamic arguments using the `-d` option:

```bash
sabcli generate-image --prompt "a cat" -d model OfficialStableDiffusion/sd_xl_base_1.0 -d images 1 --output /path/to/save

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
