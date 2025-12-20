# Standard library imports
import os
import glob
import subprocess
import re
import datetime
import logging
import urllib.request
import zipfile
from pathlib import Path

# Third party imports

# Local application imports

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FONTS_CACHE_DIR = Path.home() / ".viral-clips-fonts"
GOOGLE_FONT = "Montserrat"


def get_google_font(font_name: str) -> tuple[Path, str]:
    """
    Downloads a Google Font and returns (font_directory, ttf_filename).
    """
    FONTS_CACHE_DIR.mkdir(exist_ok=True)
    font_dir = FONTS_CACHE_DIR / font_name

    if not font_dir.exists():
        url = f"https://fonts.google.com/download?family={font_name.replace(' ', '+')}"
        zip_path = FONTS_CACHE_DIR / f"{font_name}.zip"

        logging.info(f"Downloading font: {font_name}")
        urllib.request.urlretrieve(url, zip_path)

        font_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(font_dir)
        zip_path.unlink()

    ttf_files = list(font_dir.glob("**/*.ttf"))
    if not ttf_files:
        raise FileNotFoundError(f"No TTF files found for {font_name}")

    chosen_ttf = ttf_files[0]
    for ttf in ttf_files:
        if "Regular" in ttf.name:
            chosen_ttf = ttf
            break
        elif "Bold" in ttf.name:
            chosen_ttf = ttf

    return font_dir, chosen_ttf.stem


def adjust_subtitle_timing(subtitle_path, output_path):
    """
    Adjusts subtitle timings to start from the beginning of the video.
    """
    with open(subtitle_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3})')
    first_timestamp = None
    for line in lines:
        time_match = time_pattern.findall(line)
        if time_match:
            first_timestamp = datetime.datetime.strptime(time_match[0], '%H:%M:%S,%f')
            break

    if first_timestamp is None:
        return  # No adjustment needed if no timestamps found

    start_delta = first_timestamp - datetime.datetime.strptime('00:00:00,000', '%H:%M:%S,%f')

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            new_line = line
            match = time_pattern.findall(line)
            if match:
                new_times = []
                for time_str in match:
                    original_time = datetime.datetime.strptime(time_str, '%H:%M:%S,%f')
                    new_time = original_time - start_delta
                    new_times.append(new_time.strftime('%H:%M:%S,%f')[:-3])
                new_line = time_pattern.sub(lambda x: new_times.pop(0), line)
            file.write(new_line)
    logging.info(f"Subtitles timings adjusted: {output_path}")


def convert_to_utf8(subtitle_path, output_path):
    """
    Converts subtitle file encoding to UTF-8.
    """
    try:
        with open(subtitle_path, 'r', encoding='iso-8859-1') as file:
            content = file.read()

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logging.info(f"Subtitle encoding converted: {output_path}")
    except Exception as e:
        logging.error(f"Error during subtitle conversion: {e}")


def burn_subtitles(video_path, subtitle_path, output_video_path):
    """
    Uses ffmpeg to burn subtitles into the video.
    """
    escaped_path = subtitle_path.replace(":", r"\:").replace("'", r"\'")

    if GOOGLE_FONT:
        font_dir, font_name = get_google_font(GOOGLE_FONT)
        escaped_font_dir = str(font_dir).replace(":", r"\:").replace("'", r"\'")
        subtitle_filter = f"subtitles={escaped_path}:fontsdir={escaped_font_dir}:force_style='FontName={font_name}'"
    else:
        subtitle_filter = f"subtitles={escaped_path}"

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', subtitle_filter,
        '-c:a', 'copy',
        '-y',
        output_video_path
    ]

    try:
        subprocess.run(cmd, check=True)
        logging.info(f"Subtitles have been burned into the video: {output_video_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error burning subtitles: {e}")


def process_video_and_subtitles(video_path, subtitle_path, output_folder):
    """
    Full processing of video and subtitles.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    adjusted_subtitle_path = os.path.join(output_folder, base_name + '_adjusted.srt')
    utf8_subtitle_path = os.path.join(output_folder, base_name + '_utf8.srt')
    output_video_path = os.path.join(output_folder, base_name + '_subtitled.mp4')

    adjust_subtitle_timing(subtitle_path, adjusted_subtitle_path)
    convert_to_utf8(adjusted_subtitle_path, utf8_subtitle_path)
    burn_subtitles(video_path, utf8_subtitle_path, output_video_path)

    os.remove(adjusted_subtitle_path)
    os.remove(utf8_subtitle_path)
    logging.info("Temporary subtitle files removed.")


if __name__ == "__main__":
    trimmed_videos = glob.glob('clipper_output/*_trimmed.mp4')
    subtitle_files = glob.glob('crew_output/*.srt')
    output_folder = "subtitler_output"  # Ensure this is correctly set

    # Check if output_folder exists, create it if not
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    subtitle_dict = {os.path.splitext(os.path.basename(s))[0]: s for s in subtitle_files}

    for trimmed_video in trimmed_videos:
        base_name = os.path.splitext(os.path.basename(trimmed_video))[0].replace('_trimmed', '')
        subtitle_file = subtitle_dict.get(base_name)
        if subtitle_file:
            process_video_and_subtitles(trimmed_video, subtitle_file, output_folder)
        else:
            logging.error(f"Subtitle file not found for {trimmed_video}")
