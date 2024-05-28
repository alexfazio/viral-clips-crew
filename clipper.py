import os
import re
import ffmpeg
from datetime import datetime
import glob
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_timestamp(timestamp):
    return timestamp.replace(',', '.').strip()


def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, '%H:%M:%S.%f')


def main(input_video, subtitle_file_path, output_folder):
    logging.info('~~~CLIPPER: STARTED~~~')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(subtitle_file_path, 'r') as file:
        subtitles_content = file.read()

    timestamps = re.findall(r'\d{2}:\d{2}:\d{2},\d{3}', subtitles_content)
    if not timestamps:
        logging.warning("No timestamps found in the subtitles.")
        return

    start_time = convert_timestamp(timestamps[0])
    end_time = convert_timestamp(timestamps[-1])

    # Construct the output video path using the subtitle file name as a prefix
    subtitle_base_name = os.path.splitext(os.path.basename(subtitle_file_path))[0]
    output_video_path = os.path.join(output_folder, f"{subtitle_base_name}_trimmed.mp4")

    logging.info(f"Output path: {output_video_path}")

    # Use ffmpeg to trim and crop the video to 1:1 aspect ratio
    try:
        # Get video dimensions
        probe = ffmpeg.probe(input_video)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_stream['width'])
        height = int(video_stream['height'])

        # Calculate crop dimensions for 1:1 aspect ratio
        if width > height:
            crop_size = height
            x_offset = (width - crop_size) // 2
            y_offset = 0
        else:
            crop_size = width
            x_offset = 0
            y_offset = (height - crop_size) // 2

        # Re-encode the video to ensure frame accuracy and avoid sync issues
        (
            ffmpeg
            .input(input_video, ss=start_time, to=end_time)
            .filter('crop', crop_size, crop_size, x_offset, y_offset)
            .output(output_video_path, vcodec='libx264', acodec='aac', audio_bitrate='192k', vsync='vfr', map='0:a')
            .run()
        )

    except ffmpeg.Error as e:
        logging.error(f"ffmpeg error: {e}")

    logging.info(f"Trimmed video saved to {output_video_path}")


if __name__ == "__main__":
    video_files = glob.glob('input_files/*.mp4')
    subtitle_files = glob.glob('crew_output/*.srt')
    output_folder = "clipper_output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for video_file_path in video_files:
        for subtitle_file in subtitle_files:
            main(video_file_path, subtitle_file, output_folder)
