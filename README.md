<a href="https://x.com/alxfazio" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/vcc-github-banner.png">
    <img alt="OpenAI Cookbook Logo" src="images/vcc-github-banner.png" width="400px" style="max-width: 100%; margin-bottom: 20px;">
  </picture>
</a>

Your [CrewAI](https://github.com/joaomdmoura/crewAI) Powered Video Editing Assistant

Are you a social media content curator? Skip the tedious editing process and get polished video highlights in minutes. `viral-clips-crew` watches and listens to long-form content, extracting the most striking and potentially viral segments, ready for publication on social media.

## Content Repurposing Made Easy

<div align="center">
  <img src="https://github.com/alexfazio/viral-clips-crew/assets/34505954/c69da629-06eb-4279-a5cb-0d8d7fc1dfee" width="600px" height="auto">
</div>

`viral-clips-crew` helps you repackage your valuable content in new and engaging ways to capture attention on social media and drive traffic back to the original long-form piece. Whether you're looking to refresh your own content or recycle content from other creators, this tool streamlines the process, making content repurposing effortless and efficient.

## Requirements

This project requires:

- Python 3.7+
- CrewAI
- OpenAI API key and Google Gemini API key

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

4. Update Pydantic:

    ```shell
    poetry update pydantic
    ```

5. Open `.env` and insert your OpenAI API key and Google Gemini API key.

    ```shell
   echo -e "OPENAI_API_KEY=<your-api-key>\nGEMINI_API_KEY=<your-api-key>" > .env
    ```

## Usage

After setting up, drag your desired clip into the `input_files` directory. 

**Gemini can process videos up to 1 hour in length. If you are using the OpenAI API, please ensure that the clip is less than 15 minutes in length. The current LLM context windows are approximately 15 minutes.**

Run `viral-clips-crew` using Poetry with the following command:

    ```shell
    poetry run python app.py
    ```

This will kickstart the process from beginning to completion.

Final output will be in the `subtitler_output` directory.

## Support

If you like this project and want to support it, please consider leaving a star. Every contribution helps keep the project running. Thank you!

## Troubleshooting

If you encounter a `TypeError: 'NoneType' object is not iterable`, please check the following:  
- Ensure your API keys are correctly set in the `.env` file.  
- Verify that you have enough pay-as-you-go credits in your OpenAI account and Google Cloud account.

## Note

The code for `viral-clips-crew` is intended for demonstrative purposes and is not meant for production use. The API keys are hardcoded and need to be replaced with your own. Always ensure your keys are kept secure.

## Credits

Thank you to [Rip&Tear](https://x.com/Cyb3rCh1ck3n) for his ongoing assistance in improving this tool.

## License

[MIT](https://opensource.org/licenses/MIT)

Copyright (c) 2024-present, Alex Fazio

---

[![Watch the video](https://i.imgur.com/TBD2bvj.png)](https://x.com/alxfazio/status/1791863931931078719)
