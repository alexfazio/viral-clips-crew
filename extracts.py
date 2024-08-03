# Standard library imports
import sys
import json
import os
from textwrap import dedent
import logging
from pathlib import Path

# Third party imports
from openai import OpenAI
from dotenv import load_dotenv

# Local application imports

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

def get_whisper_output():
    whisper_output_dir = Path('whisper_output')
    if not whisper_output_dir.exists():
        logging.error(f"Directory not found: {whisper_output_dir}")
        return None, None

    srt_files = list(whisper_output_dir.glob('*.srt'))
    txt_files = list(whisper_output_dir.glob('*.txt'))

    if not srt_files or not txt_files:
        logging.warning("No .srt or .txt files found in the whisper_output directory.")
        return None, None

    with open(txt_files[0], 'r') as file:
        transcript = file.read()

    with open(srt_files[0], 'r') as file:
        subtitles = file.read()

    return transcript, subtitles

def call_openai_api(transcript):
    logging.info("STARTING call_openai_api")

    prompt = dedent(f"""
        Here is the full transcript from the video:
        
        <transcript>
        {transcript}
        </transcript>
        
        Your task is to identify the three 1-minute long clips from this video that have the highest potential to go viral on social media.  
        
        Carefully read through the entire transcript above, looking for the most powerful, emotionally impactful, surprising, thought-provoking or otherwise memorable moments. Select three 1-minute long segments centered around those powerful moments that you think have the best chance of getting widely shared and going viral.
        
        For each clip you select, extract the full text of the selected 1-minute segment from the transcript. 
        
        Order the three clips from most to least viral potential based on your assessment.
        
        Format the final output as a JSON object containing an ordered list of the selected clips, each with its extracted text. The JSON object should look like this:
    
        {{
        "clips": [
            {{
            "rank": 1,
            "text": "<extracted text of clip 1>"
            }},
            {{
            "rank": 2, 
            "text": "<extracted text of clip 2>"
            }},
            {{
            "rank": 3,
            "text": "<extracted text of clip 3>"
            }}
        ]
        }}
    
        Return nothing else but the raw content of the JSON object itself - no comments, no extra text. Just the JSON.
    """)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        response_data = json.loads(response.choices[0].message.content)
        clip_texts = [clip['text'] for clip in response_data['clips']]

        logging.info("[START] extracts.py RESPONSE")
        print(json.dumps(response_data, indent=4))
        logging.info("[END] extracts.py RESPONSE")
        return clip_texts
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return []

def save_response_to_file(response, output_path):
    try:
        # Since response is a list of clip texts, we need to format it correctly
        response_content = {"clips": [{"rank": i+1, "text": clip} for i, clip in enumerate(response)]}
        
        with open(output_path, 'w') as f:
            json.dump(response_content, f, indent=4)

        logging.info(f"Response saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving response to file: {e}")

def main():
    logging.info('STARTING extracts.py')

    transcript, subtitles = get_whisper_output()
    if transcript is None or subtitles is None:
        return None

    response = call_openai_api(transcript)
    if response:
        output_dir = Path('crew_output')
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / 'api_response.json'
        save_response_to_file(response, output_path)
    return response

if __name__ == "__main__":
    main()