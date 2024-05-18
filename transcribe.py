import os, re
import torch
from pathlib import Path
from pytube import YouTube

import whisper
from whisper.utils import get_writer


def main(file):
    def transcribe_file(model, plain, srt, vtt, tsv, file):
        """
        Runs Whisper on an audio file

        Parameters
        ----------
        model: Whisper
            The Whisper model instance.

        file: str
            The file path of the file to be transcribed.

        plain: bool
            Whether to save the transcription as a text file or not.

        srt: bool
            Whether to save the transcription as an SRT file or not.

        vtt: bool
            Whether to save the transcription as a VTT file or not.

        tsv: bool
            Whether to save the transcription as a TSV file or not.

        Returns
        -------
        A dictionary containing the resulting text ("text") and segment-level details ("segments"), and
        the spoken language ("language"), which is detected when `decode_options["language"]` is None.
        """
        input_file_path = Path(file)
        print(f"Transcribing file: {input_file_path}\n")

        # Ensure the output directory exists
        output_dir = Path("whisper_output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run Whisper
        result = model.transcribe(str(input_file_path), fp16=False, verbose=False, language="en")

        output_file_name = input_file_path.stem

        if plain:
            txt_path = output_dir / f"{output_file_name}.txt"
            print(f"\nCreating text file")

            with open(txt_path, "w", encoding="utf-8") as txt:
                txt.write(result["text"])

            transcript = result["text"]

        if srt:
            print(f"\nCreating SRT file")
            srt_writer = get_writer("srt", str(output_dir))
            srt_writer(result, output_file_name)

            # Construct the SRT file path manually
            srt_path = output_dir / f"{output_file_name}.srt"

            # Read the SRT subtitles from the generated file
            with open(srt_path, "r", encoding="utf-8") as srt_file:
                subtitles = srt_file.read()

        if vtt:
            print(f"\nCreating VTT file")
            vtt_writer = get_writer("vtt", str(output_dir))
            vtt_writer(result, output_file_name)

        if tsv:
            print(f"\nCreating TSV file")

            tsv_writer = get_writer("tsv", str(output_dir))
            tsv_writer(result, output_file_name)

        return result, transcript, subtitles

    ### ➡️ Output Options

    # @markdown Select the source of the audio/video file to be transcribed
    input_format = "local"  # @param ["youtube", "gdrive", "local"]

    # @markdown Click here if you'd like to save the transcription as text file
    plain = True  # @param {type:"boolean"}

    # @markdown Click here if you'd like to save the transcription as an SRT file
    srt = True  # @param {type:"boolean"}

    # @markdown Click here if you'd like to save the transcription as a VTT file
    vtt = False  # @param {type:"boolean"}

    # @markdown Click here if you'd like to save the transcription as a TSV file
    tsv = False  # @param {type:"boolean"}

    ### 👋 Whisper configuration

    # Use CUDA, if available
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # Load the desired model
    model = whisper.load_model("medium.en").to(DEVICE)

    result, transcript, subtitles = transcribe_file(model, plain, srt, vtt, tsv, file)

    return transcript, subtitles


if __name__ == "__main__":
    import os
    input_folder = 'input_files'
    if os.path.exists(input_folder):
        for filename in os.listdir(input_folder):
            if filename.endswith(".mp4"):
                file_path = os.path.join(input_folder, filename)
                print(f"Processing file: {file_path}")
                main(file_path)
    else:
        print(f"Input folder not found: {input_folder}")
