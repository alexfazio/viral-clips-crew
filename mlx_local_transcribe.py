# Standard library imports
from pathlib import Path
import os
import warnings
import logging
import subprocess
import numpy as np

# Third party imports
import mlx.core as mx
import mlx_whisper

# Local application imports
from utils import wait_for_file

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
warnings.filterwarnings("ignore")

def prepare_audio(audio_path: str) -> mx.array:
    command = [
        "ffmpeg",
        "-i", audio_path,
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-"
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    audio_data, _ = process.communicate()
    
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    audio_array = audio_array.astype(np.float32) / 32768.0
    
    return mx.array(audio_array)

def transcribe_file(model_path, srt, plain, file):
    input_file_path = Path(file)
    logging.info(f"Transcribing file: {input_file_path}\n")

    # Ensure the output directory exists
    output_dir = Path("whisper_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare audio
    audio = prepare_audio(str(input_file_path))

    # Run MLX Whisper
    result = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo=model_path,
        fp16=False,
        verbose=True
    )

    output_file_name = input_file_path.stem

    transcript = result["text"]
    subtitles = ""

    if plain:
        txt_path = output_dir / f"{output_file_name}.txt"
        logging.info(f"Creating text file: {txt_path}")

        with open(txt_path, "w", encoding="utf-8") as txt:
            txt.write(transcript)

    if srt:
        logging.info(f"Creating SRT file")
        srt_path = output_dir / f"{output_file_name}.srt"
        write_subtitles(result["segments"], "srt", str(srt_path))

        # Read the SRT subtitles from the generated file
        with open(srt_path, "r", encoding="utf-8") as srt_file:
            subtitles = srt_file.read()

    return result, transcript, subtitles

def write_subtitles(segments, format, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        if format == "srt":
            for i, segment in enumerate(segments, start=1):
                f.write(f"{i}\n")
                start = f"{int(segment['start'] // 3600):02d}:{int(segment['start'] % 3600 // 60):02d}:{segment['start'] % 60:06.3f}"
                end = f"{int(segment['end'] // 3600):02d}:{int(segment['end'] % 3600 // 60):02d}:{segment['end'] % 60:06.3f}"
                f.write(f"{start.replace('.', ',')} --> {end.replace('.', ',')}\n")
                f.write(f"{segment['text'].strip()}\n\n")

def transcribe_main(file):
    # specify the type of file outputs you need from MLX Whisper
    plain = True
    srt = True

    # MLX Whisper configuration
    MODEL_PATH = "mlx-community/whisper-large-v3-mlx"

    result, transcript, subtitles = transcribe_file(MODEL_PATH, srt, plain, file)

    return transcript, subtitles

def local_whisper_process(input_folder, crew_output_folder, transcript=None, subtitles=None,
                          transcribe_flag=True):
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_video_path = os.path.join(input_folder, filename)
            logging.info(f"Processing video: {input_video_path}")

            if transcribe_flag:
                if transcript and subtitles:
                    initial_srt_path = os.path.join(crew_output_folder,
                                                    f"{os.path.splitext(filename)[0]}_subtitles.srt")
                    with open(initial_srt_path, 'w') as srt_file:
                        srt_file.write(subtitles)
                else:
                    full_transcript, full_subtitles = transcribe_main(input_video_path)
                    initial_srt_path = os.path.join(crew_output_folder,
                                                    f"{os.path.splitext(filename)[0]}_subtitles.srt")
                    with open(initial_srt_path, 'w') as srt_file:
                        srt_file.write(full_subtitles)
            else:
                initial_srt_path = os.path.join(crew_output_folder, f"{os.path.splitext(filename)[0]}.srt")

            if wait_for_file(initial_srt_path):
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
                    for srt_filename in sorted(os.listdir(crew_output_folder)):
                        if srt_filename.startswith("new_file_return_subtitles") and srt_filename.endswith(".srt"):
                            subtitle_file_path = os.path.join(crew_output_folder, srt_filename)
                else:
                    logging.error("No .srt or .txt files found in the whisper_output directory.")
            else:
                logging.error(f"Failed to verify the readiness of subtitles file: {initial_srt_path}")

    logging.info(f"mlx_local_transcribe.py completed")

if __name__ == "__main__":
    input_folder = 'input_files'
    crew_output_folder = 'crew_output'

    if os.path.exists(input_folder):
        local_whisper_process(input_folder, crew_output_folder)
    else:
        logging.error(f"Input folder not found: {input_folder}")