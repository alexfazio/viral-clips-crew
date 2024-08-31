# Standard library imports
import os
import warnings
import re
from datetime import datetime
import glob
import logging

# Third party imports
import ffmpeg

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings("ignore")


def convert_timestamp(timestamp):
    return timestamp.replace(',', '.').strip()


def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, '%H:%M:%S.%f')


def get_aspect_ratio_choice():
    while True:
        choice = input("Choose aspect ratio for all videos: (1) Keep as original, (2) 1:1 (square): ")
        if choice in ['1', '2']:
            return choice
        print("Invalid choice. Please enter 1 or 2.")


def process_video(input_video, subtitle_file_path, output_folder, aspect_ratio_choice):
    logging.info('~~~CLIPPER: PROCESSING VIDEO~~~')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(subtitle_file_path, 'r') as file:
        subtitles_content = file.read()

    assert subtitles_content != "", "clipper.py received an empty subtitles file"

    timestamps = re.findall(r'\d{2}:\d{2}:\d{2},\d{3}', subtitles_content)
    if not timestamps:
        logging.warning("No timestamps found in the subtitles.")
        return

    start_time = convert_timestamp(timestamps[0])
    end_time = convert_timestamp(timestamps[-1])

    # Log the extracted start and end times
    logging.info(f"Extracted Start Time: {start_time}")
    logging.info(f"Extracted End Time: {end_time}")

    # Calculate duration
    start_datetime = parse_timestamp(start_time)
    end_datetime = parse_timestamp(end_time)
    duration = end_datetime - start_datetime
    duration_seconds = duration.total_seconds()

    # Log the calculated duration
    logging.info(f"Calculated Duration: {duration_seconds:.2f} seconds")

    # Check if duration is less than 30 seconds or exceeds 2 minutes and 30 seconds
    if duration_seconds < 30:
        logging.warning(
            f"Video fragment duration ({duration_seconds:.2f} seconds) is less than 30 seconds. Skipping this subtitle file.")
        return
    if duration_seconds > 150:  # 150 seconds = 2 minutes 30 seconds
        logging.warning(
            f"Video fragment duration ({duration_seconds:.2f} seconds) exceeds 2 minutes 30 seconds. Skipping this subtitle file.")
        return

    # Construct the output video path using the subtitle file name as a prefix
    subtitle_base_name = os.path.splitext(os.path.basename(subtitle_file_path))[0]
    output_video_path = os.path.join(output_folder, f"{subtitle_base_name}_trimmed.mp4")

    logging.info(f"Output path: {output_video_path}")

    try:
        # Get video dimensions
        probe = ffmpeg.probe(input_video)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_stream['width'])
        height = int(video_stream['height'])

        # Log video dimensions
        logging.info(f"Video Width: {width}, Video Height: {height}")

        # Initialize ffmpeg input
        input_stream = ffmpeg.input(input_video, ss=start_time, t=duration_seconds)

        if aspect_ratio_choice == '2':  # 1:1 (square)
            # Calculate crop dimensions for 1:1 aspect ratio
            if width > height:
                crop_size = height
                x_offset = (width - crop_size) // 2
                y_offset = 0
            else:
                crop_size = width
                x_offset = 0
                y_offset = (height - crop_size) // 2

            # Apply crop filter
            video = input_stream.video.filter('crop', crop_size, crop_size, x_offset, y_offset)
        else:
            video = input_stream.video

        audio = input_stream.audio

        # Re-encode the video
        output = ffmpeg.output(video, audio, output_video_path,
                               vcodec='libx264', acodec='aac',
                               audio_bitrate='192k',
                               **{'vsync': 'vfr'})

        ffmpeg.run(output, overwrite_output=True)
        logging.info(f"Trimmed video saved to {output_video_path}")

    except ffmpeg.Error as e:
        logging.error(f"ffmpeg error: {str(e)}")


def main(input_video, subtitle_file_path, output_folder, aspect_ratio_choice=None):
    if aspect_ratio_choice is None:
        aspect_ratio_choice = get_aspect_ratio_choice()
    process_video(input_video, subtitle_file_path, output_folder, aspect_ratio_choice)


if __name__ == "__main__":
    video_files = glob.glob('input_files/*.mp4')
    subtitle_files = glob.glob('crew_output/*.srt')
    output_folder = "clipper_output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Ask for aspect ratio choice once
    aspect_ratio_choice = get_aspect_ratio_choice()

    for video_file_path in video_files:
        for subtitle_file in subtitle_files:
            process_video(video_file_path, subtitle_file, output_folder, aspect_ratio_choice)