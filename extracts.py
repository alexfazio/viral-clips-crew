import sys
import json
import os
from openai import OpenAI
from textwrap import dedent
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

def call_openai_api():
    print("~~~STARTING call_openai_api~~~")

    # Check if the whisper_output directory exists and contains .srt and .txt files
    whisper_output_dir = 'whisper_output'
    if os.path.exists(whisper_output_dir):
        srt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.srt')]
        txt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.txt')]

        if srt_files and txt_files:
            # Assuming the first .srt and .txt files are the ones to process
            subtitles_file = os.path.join(whisper_output_dir, srt_files[0])
            transcript_file = os.path.join(whisper_output_dir, txt_files[0])

            with open(transcript_file, 'r') as file:
                transcript = file.read()

            with open(subtitles_file, 'r') as file:
                subtitles = file.read()
        else:
            print("No .srt or .txt files found in the whisper_output directory.")
            return []
    else:
        print(f"Directory not found: {whisper_output_dir}")
        sys.exit(1)

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
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the text from the response
        response_data = json.loads(response.choices[0].message.content)
        clip_texts = [clip['text'] for clip in response_data['clips']]

        print("~~~EXTRACTS.py RESPONSE~~~")
        print("```")
        print(json.dumps(response_data, indent=4))
        print("```")
        print("~~~EXTRACTS.py RESPONSE~~~")
        return clip_texts
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []

def save_response_to_file(response, output_path):
    try:
        # Since response is a list of clip texts, we need to format it correctly
        response_content = {"clips": [{"rank": i+1, "text": clip} for i, clip in enumerate(response)]}
        
        with open(output_path, 'w') as f:
            json.dump(response_content, f, indent=4)
        
        print(f"Response saved to {output_path}")
    except Exception as e:
        print(f"Error saving response to file: {e}")

def main():
    print("~~~STARTING EXTRACTS.py~~~")
    print("~~~STARTING EXTRACTS.py~~~")
    print("~~~STARTING EXTRACTS.py~~~")

    response = call_openai_api()
    if response:
        # Use the relative directory
        output_dir = 'crew_output'
        output_path = os.path.join(output_dir, 'api_response.json')
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        save_response_to_file(response, output_path)
    return response

if __name__ == "__main__":
    main()
