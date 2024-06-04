import logging
from pytube import YouTube
from pathlib import Path
import xml.etree.ElementTree as ElementTree
from datetime import timedelta
import os


def get_video_from_youtube_url(url: str, save_path: str = None) -> tuple:
    yt = YouTube(url)
    save_path = Path(save_path) if save_path else Path(".")
    filename = yt.title.replace(" ", "_")  # Replace spaces with underscores to avoid issues
    s = (yt.streams.filter(progressive=True, file_extension='mp4')
         .order_by('resolution').desc().first()
         )
    video_path = s.download(output_path=save_path, filename=filename)
    video_file = Path(video_path)

    # Ensure the file has a .mp4 extension
    if not video_file.suffix == '.mp4':
        new_video_file = video_file.with_suffix('.mp4')
        video_file.rename(new_video_file)
        video_file = new_video_file

    captions = yt.captions

    return captions, video_file

# TODO: fix below function

def pytube_to_srt(yt, filename: str):
    """Takes a pytube YouTube object and filename, tries to download English or auto-generated English captions."""
    output_dir = Path("./whisper_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.debug("Printing available captions START")
    print(yt.captions)
    logging.debug("Printing available captions END")

    # Try to get manually created English captions first
    caption = yt.captions.get_by_language_code('a.en')
    # if not caption:
    #     # If not available, try to get auto-generated English captions
    #     logging.debug("No manually created English captions found, trying auto-generated captions.")
    #     caption = yt.captions.get_by_language_code('a.en')

    if not caption:
        # If no English captions are available at all
        logging.warning("No English captions (manual or auto-generated) found.")
        return None, None

    logging.debug("Captions found, generating SRT captions.")
    srt_captions = caption.generate_srt_captions()
    srt_file_path = output_dir / f"{filename.stem}.srt"

    logging.debug(f"Writing SRT file to {srt_file_path}.")
    with open(srt_file_path, 'w', encoding='utf-8') as f:
        f.write(srt_captions)

    return srt_captions, srt_file_path


def pytube_to_txt(srt_captions: str) -> None:
    """Converts SRT captions into plain text and writes them to a .txt file."""
    # Directory setup
    output_dir = Path("./caption_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse SRT captions to extract textual content
    lines = srt_captions.split('\n')
    plain_text_lines = []
    for line in lines:
        # Filter out numeric-only lines and timestamp lines
        if not line.strip().isdigit() and '-->' not in line:
            plain_text_lines.append(line.strip())

    # Combine text lines into a single string with spaces
    plain_text = ' '.join(plain_text_lines).replace('  ', ' ')

    # Write the plain text to a file if there are captions
    if plain_text_lines:
        txt_file_path = output_dir / "captions.txt"
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        logging.info(f"Captions written to {txt_file_path}")
    else:
        logging.warning("No captions available to write.")

def format_time(seconds):
    td = str(timedelta(seconds=seconds))
    parts = td.split(':')
    hours, minutes = parts[0], parts[1]
    if '.' in parts[2]:
        seconds, milliseconds = parts[2].split('.')
    else:
        seconds, milliseconds = parts[2], '000'
    milliseconds = milliseconds[:3].ljust(3, '0')  # Ensure milliseconds are exactly 3 digits
    return "{:02}:{:02}:{:02},{:03}".format(int(hours), int(minutes), int(seconds), int(milliseconds))


def main(url, save_path):
    yt, video_file = get_video_from_youtube_url(url, save_path)
    srt_captions, srt_file_path = pytube_to_srt(yt, video_file)
    if srt_captions:
        pytube_to_txt(srt_captions)

    # yt, video_file = get_video_from_youtube_url(url, save_path)
    # srt_captions, srt_file_path = pytube_to_srt(yt, video_file)
    # if srt_captions:
    #     pytube_to_txt(srt_captions)


#  plain_text = pytube_to_txt(srt_captions)

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    save_path = "./input_files"
    print(get_video_from_youtube_url(url, save_path))
