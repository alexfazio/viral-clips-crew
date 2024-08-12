# Standard library imports
import os
import warnings
import logging
from pathlib import Path
from send2trash import send2trash

# Third party imports
from dotenv import load_dotenv

# Local application imports
import clipper
import subtitler
import crew
from ytdl import main as ytdl_main
from local_transcribe import local_whisper_process
import extracts

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# List of required environment variables
required_vars = ['OPENAI_API_KEY', 'GEMINI_API_KEY']

"""
This for loop checks if the required environment variables are set. 
If any of the required environment variables are set to 'None', an EnvironmentError is raised.
"""
for var in required_vars:
    value = os.getenv(var)
    if value is None or value == 'None':
        raise EnvironmentError(f"Required environment variable {var} is not set or is set to 'None'.")

def get_aspect_ratio_choice():
    while True:
        choice = input("Choose aspect ratio for all videos: (1) Keep as original, (2) 1:1 (square): ")
        if choice in ['1', '2']:
            return choice
        print("Invalid choice. Please enter 1 or 2.")

def clean_whisper_output():
    whisper_output_folder = './whisper_output'
    for filename in os.listdir(whisper_output_folder):
        file_path = os.path.join(whisper_output_folder, filename)
        try:
            if os.path.isfile(file_path):
                send2trash(file_path)
                logging.info(f"Moved {file_path} to trash")
        except Exception as e:
            logging.error(f"Error while moving {file_path} to trash: {e}")

def main():
    input_folder = './input_files'
    output_video_folder = './clipper_output'
    crew_output_folder = './crew_output'
    whisper_output_folder = './whisper_output'
    subtitler_output_folder = './subtitler_output'

    # Ensure all necessary directories exist
    for folder in [input_folder, output_video_folder, crew_output_folder, whisper_output_folder, subtitler_output_folder]:
        os.makedirs(folder, exist_ok=True)

    # User selection
    while True:
        logging.info("Please select an option to proceed:")
        logging.info("1: Submit a YouTube Video Link")
        logging.info("2: Use an existing video file")
        choice = input("Please choose either option 1 or 2: ")

        if choice == '1':
            logging.info("Submitting a YouTube Video Link")
            url = input("Enter the YouTube URL: ")
            ytdl_main(url, input_folder, whisper_output_folder, whisper_output_folder)
            break
        elif choice == '2':
            logging.info("Using an existing video file")
            if not os.listdir(input_folder):
                logging.error(f"No video files found in the folder: {input_folder}")
                continue
            clean_whisper_output()  # Clean whisper_output folder
            local_whisper_process(input_folder, whisper_output_folder)
            break
        else:
            logging.info("Invalid choice. Please try again.")

    # Get aspect ratio choice
    aspect_ratio_choice = get_aspect_ratio_choice()

    # After processing with ytdl or local_whisper_process
    extracts_data = extracts.main()
    if extracts_data is None:
        logging.error("Failed to generate extracts. Exiting.")
        return

    # Process with crew.py
    crew.main(extracts_data)

    # Process with clipper.py
    input_folder_path = Path(input_folder)
    crew_output_folder_path = Path(crew_output_folder)
    output_video_folder_path = Path(output_video_folder)

    for video_file in input_folder_path.glob('*.mp4'):
        for srt_file in crew_output_folder_path.glob('*.srt'):
            clipper.main(str(video_file), str(srt_file), str(output_video_folder_path), aspect_ratio_choice)
            logging.info(f"Processed {video_file} with {srt_file}")

    # Process with subtitler.py
    for video_file in output_video_folder_path.glob('*_trimmed.mp4'):
        base_name = video_file.stem.replace('_trimmed', '')
        srt_file = crew_output_folder_path / f"{base_name}.srt"
        if srt_file.exists():
            subtitler.process_video_and_subtitles(str(video_file), str(srt_file), subtitler_output_folder)
            logging.info(f"Added subtitles to {video_file}")
        else:
            logging.warning(f"No matching subtitle file found for {video_file}")

    logging.info(f"All videos processed. Final output saved in {subtitler_output_folder}")

if __name__ == "__main__":
    main()

# TODO: Change the options to: 1. Download YouTube video and transcribe locally 2. Download YouTube video and use remote transcript 3. Use existing video file to transcribe locally
# TODO: Add an API key validator before proceeding with the execution to avoid discovering that the API key is invalid during later stages of the process.
# TODO: Request the aspect ratio input before initiating the local transcription process.