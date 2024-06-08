# Standard library imports
import os
import warnings
import logging

# Local application
import extracts
import subtitler
import transcribe
import crew
from utils import wait_for_file
from clip_sub import clip_and_sub

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings("ignore")

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
