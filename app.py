# Standard library imports
import os
import warnings
import logging
from pathlib import Path

# Third party imports
from dotenv import load_dotenv

# Local application imports
import clipper
import subtitler
from ytdl import main as ytdl_main
from local_transcribe import local_whisper_process

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


# def clip(input_video_path, subtitle_file, output_video_folder):

# def sub(subtitle_file):

def main():
    input_folder = './input_files'
    output_video_folder = './clipper_output'
    crew_output_folder = './crew_output'
    whisper_output_folder = './whisper_output'

    # User selection
    def user_prompt():
        """Prompt the user to select an option to proceed"""
        logging.info("Please select an option to proceed:")
        logging.info("1: Submit a YouTube Video Link")
        logging.info("2: Use an existing video file")

    def user_choice():
        """Get the user's choice"""
        choice = input("Please choose either option 1 or 2: ")
        return choice

    while True:
        user_prompt()  # Display the prompt before asking for the choice
        choice = user_choice()

        if choice == '1':
            logging.info("Submitting a YouTube Video Link")
            # Download video from YouTube
            url = input("Enter the YouTube URL: ")
            ytdl_main(url, input_folder, whisper_output_folder, whisper_output_folder)
            transcribe_flag = False
            break
        elif choice == '2':
            logging.info("Using an existing video file")
            if not os.listdir(input_folder):
                logging.error(f"No video files found in the folder: {input_folder}")
                continue
            transcribe_flag = True
            break
        else:
            logging.info("Invalid choice. Please try again.")

    try:
        os.makedirs(output_video_folder, exist_ok=True)
        os.makedirs(crew_output_folder, exist_ok=True)
        os.makedirs(whisper_output_folder, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating directories: {e}")
        return

    # converting paths to Path paths for glob

    input_folder_path = Path(input_folder)
    whisper_output_folder_path = Path(whisper_output_folder)
    output_video_folder_path = Path(output_video_folder)

    # local_whisper.py

    local_whisper_process(input_folder, output_video_folder, crew_output_folder, transcribe_flag=transcribe_flag)

    # clipper.py

    for video_file in input_folder_path.glob('*.mp4'):
        for srt_file in whisper_output_folder_path.glob('*.srt'):
            # Process each video and subtitle pair
            clipper.main(video_file, srt_file, output_video_folder_path)
            print(f"Processed {video_file}")

    # subtitler.py

    # output_video_folder in this case is clipper_output
    for video_file in output_video_folder_path.glob('*.mp4'):
        for srt_file in whisper_output_folder_path.glob('*.srt'):
            trimmed_video_path = os.path.join(output_video_folder_path,
                                              f"{os.path.splitext(os.path.basename(srt_file))[0]}_trimmed.mp4")
            subtitler.process_video_and_subtitles(trimmed_video_path, srt_file, 'subtitler_output')
            subtitled_video_path = os.path.join('subtitler_output',
                                                f"{os.path.splitext(os.path.basename(srt_file))[0]}_subtitled.mp4")

    logging.info(f"Video processed and saved to {subtitled_video_path}")


if __name__ == "__main__":
    main()
