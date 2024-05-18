Here's an improved version of that part:

# viral-clips-crew (alpha)

<div align="center">
  <img src="https://github.com/alexfazio/viral-clips-crew/assets/34505954/a065a40a-47c2-44fd-8c71-635dcd1eb658" width="400px" height="auto">
</div>

# `viral-clips-crew` Your CrewAI Powered Video Editing Assistant

Are you a social media content curator? Skip the tedious editing process and get polished video highlights in minutes. `viral-clips-crew` watches and listens to long-form content, extracting the most striking and potentially viral segments, ready for publication on social media.

## Content Repurposing Made Easy

`viral-clips-crew` helps you repackage your valuable content in new and engaging ways to capture attention on social media and drive traffic back to the original long-form piece. Whether you're looking to refresh your own content or recycle content from other creators, this tool streamlines the process, making content repurposing effortless and efficient.


## Requirements

This project requires:

- Python 3.7+
- CrewAI
- OpenAI API key

All required Python libraries are listed in `pyproject.toml`.

## Installation

1. Clone this repository to your local machine:

```shell
git clone https://github.com/alexfazio/viral-clips-crew.git
```

2. Install Poetry to automatically manage project dependencies:

```shell
pip install poetry
```

3. Install the required Python packages using Poetry:

```shell
poetry install
```

4. Open `.env` and insert your OpenAI API key.

## Usage

After setting up, drag your desired clip into the `input_files` directory.

Run `viral-clips-crew` using Poetry with the following command:

```shell
poetry run python app.py
```

This will kickstart the process from beginning to completion.

## Support

If you like this project and want to support it, please consider leaving a star. Every contribution helps keep the project running. Thank you!

## Note

The code for `viral-clips-crew` is intended for demonstrative purposes and is not meant for production use. The API keys are hardcoded and need to be replaced with your own. Always ensure your keys are kept secure.

## License

This project is licensed under the terms of the MIT license.

