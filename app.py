import warnings
warnings.filterwarnings("ignore")

import os
import time
from dotenv import load_dotenv
import transcribe
import crew
import extracts  # Import extracts module
import trimmer
import subtitler

# Load environment variables
load_dotenv()

def file_ready(filename):
    """Check if the file is ready by attempting to append to it."""
    try:
        with open(filename, 'ab'):
            return True
    except IOError:
        return False

def wait_for_file(filename, timeout=30):
    """Wait for a file to be fully written and ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if file_ready(filename):
            return True
        time.sleep(1)
    return False

def wait_for_file_existence(filepath, timeout=30):
    """Wait for a file to be created and exist."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(filepath):
            return True
        time.sleep(1)
    return False

def process_subtitles(input_video_path, subtitle_file, output_video_folder):
    """Process a single subtitle file to create a trimmed and subtitled video."""
    # Step 1: Trim the video
    trimmed_video_path = os.path.join(output_video_folder,
                                      f"{os.path.splitext(os.path.basename(subtitle_file))[0]}_trimmed.mp4")
    trimmer.main(input_video_path, subtitle_file, output_video_folder)

    # Wait for the trimmed video file to be created
    if not wait_for_file_existence(trimmed_video_path, timeout=60):
        print(f"Error: Trimmed video file not found: {trimmed_video_path}")
        return

    # Step 2: Apply subtitles
    subtitled_video_path = os.path.join('subtitler_output',
                                        f"{os.path.splitext(os.path.basename(subtitle_file))[0]}_subtitled.mp4")
    subtitler.process_video_and_subtitles(trimmed_video_path, subtitle_file, 'subtitler_output')

    print(f"Video processed and saved to {subtitled_video_path}")

def main():
    input_folder = 'input_files'
    output_video_folder = 'clipper_output'
    crew_output_folder = 'crew_output'

    # Ensure output directories exist
    os.makedirs(output_video_folder, exist_ok=True)
    os.makedirs(crew_output_folder, exist_ok=True)

    # Process each video file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_video_path = os.path.join(input_folder, filename)
            print(f"Processing video: {input_video_path}")

            # Transcription and subtitle generation
            full_transcript, full_subtitles = transcribe.main(input_video_path)
            print("Transcription and subtitles generated.")

            initial_srt_path = os.path.join(crew_output_folder, f"{os.path.splitext(filename)[0]}_subtitles.srt")
            with open(initial_srt_path, 'w') as srt_file:
                srt_file.write(full_subtitles)

            if wait_for_file(initial_srt_path):
                # Call extracts.py and get the response
                extracts_response = extracts.main()
                print("Extracts processed.")

                # Pass the extracts response to crew.main
                crew.main(extracts_response, full_subtitles)  # Pass only the required arguments
                print("Processed with crew.")

                # Process each generated .srt file
                for srt_filename in sorted(os.listdir(crew_output_folder)):
                    if srt_filename.startswith("new_file_return_subtitles") and srt_filename.endswith(".srt"):
                        subtitle_file_path = os.path.join(crew_output_folder, srt_filename)
                        process_subtitles(input_video_path, subtitle_file_path, output_video_folder)
            else:
                print(f"Failed to verify the readiness of subtitles file: {initial_srt_path}")

if __name__ == "__main__":
    main()