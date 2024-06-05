# Standard library imports
import os
import warnings
import logging

# Related third party imports
from dotenv import load_dotenv
import lockfile

# Local application/library specific imports
import clipper
import crew
import extracts
import subtitler
import transcribe
from ytdl import main as ytdl_main

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


def wait_for_file(filepath):
    """
    This function waits for a file to be available before proceeding.

    Args:
        filepath: Path to the file to wait for
    """
    lock = lockfile.FileLock(filepath)
    while not lock.i_am_locking():
        try:
            lock.acquire(timeout=1)  # wait for 1 second
        except lockfile.LockTimeout:
            pass
    return True


def clip_and_sub(input_video_path, subtitle_file, output_video_folder):
    """This function processes the subtitles and generates a subtitled video

    Args:
        input_video_path:
        subtitle_file:
        output_video_folder:
    """
    trimmed_video_path = os.path.join(output_video_folder,
                                      f"{os.path.splitext(os.path.basename(subtitle_file))[0]}_trimmed.mp4")
    clipper.main(input_video_path, subtitle_file, output_video_folder)

    if not wait_for_file(trimmed_video_path):
        logging.error(f"Error: Trimmed video file not found: {trimmed_video_path}")
        return

    subtitled_video_path = os.path.join('subtitler_output',
                                        f"{os.path.splitext(os.path.basename(subtitle_file))[0]}_subtitled.mp4")
    subtitler.process_video_and_subtitles(trimmed_video_path, subtitle_file, 'subtitler_output')

    logging.info(f"Video processed and saved to {subtitled_video_path}")


def local_whisper_process(input_folder, output_video_folder, crew_output_folder, transcript=None, subtitles=None, transcribe_flag=True):
    """Process each video file in the input folder

    Args:
        input_folder:
        output_video_folder:
        crew_output_folder:
        transcript:
        subtitles:
        transcribe_flag:
    """
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_video_path = os.path.join(input_folder, filename)
            logging.info(f"Processing video: {input_video_path}")

            if transcribe_flag:
                if transcript and subtitles:
                    initial_srt_path = os.path.join(crew_output_folder, f"{os.path.splitext(filename)[0]}_subtitles.srt")
                    with open(initial_srt_path, 'w') as srt_file:
                        srt_file.write(subtitles)
                else:
                    full_transcript, full_subtitles = transcribe.main(input_video_path)
                    initial_srt_path = os.path.join(crew_output_folder, f"{os.path.splitext(filename)[0]}_subtitles.srt")
                    with open(initial_srt_path, 'w') as srt_file:
                        srt_file.write(full_subtitles)
            else:
                initial_srt_path = os.path.join(crew_output_folder, f"{os.path.splitext(filename)[0]}.srt")

            if wait_for_file(initial_srt_path):
                extracts_response = extracts.main()
                logging.info("Extracts processed.")
                whisper_output_dir = 'whisper_output'
                srt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.srt')]
                txt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.txt')]

                if srt_files and txt_files:
                    subtitles_file = os.path.join(whisper_output_dir, srt_files[0])
                    transcript_file = os.path.join(whisper_output_dir, txt_files[0])
                    with open(transcript_file, 'r') as file:
                        transcript = file.read()
                    with open(subtitles_file, 'r') as file:
                        subtitles = file.read()
                    crew.main(extracts_response, subtitles)
                    logging.info("Processed with crew.")
                    for srt_filename in sorted(os.listdir(crew_output_folder)):
                        if srt_filename.startswith("new_file_return_subtitles") and srt_filename.endswith(".srt"):
                            subtitle_file_path = os.path.join(crew_output_folder, srt_filename)
                            clip_and_sub(input_video_path, subtitle_file_path, output_video_folder)
                else:
                    logging.error("No .srt or .txt files found in the whisper_output directory.")
            else:
                logging.error(f"Failed to verify the readiness of subtitles file: {initial_srt_path}")


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

    local_whisper_process(input_folder, output_video_folder, crew_output_folder, transcribe_flag=transcribe_flag)


if __name__ == "__main__":
    main()
