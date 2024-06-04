import logging
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(yt_vid_url):
    # Step 2: Create a regex pattern to match YouTube video IDs
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'

    # Step 3: Extract and return the video ID
    match = re.search(pattern, yt_vid_url)
    if match:
        return match.group(1)
    else:
        return None

def yt_vid_id_to_srt(yt_video_id, srt_save_path):
    transcript = YouTubeTranscriptApi.get_transcript(yt_video_id)

    srt_content = []
    for i, entry in enumerate(transcript):
        start = entry['start']
        duration = entry['duration']
        text = entry['text']

        start_hours, start_remainder = divmod(start, 3600)
        start_minutes, start_seconds = divmod(start_remainder, 60)
        start_milliseconds = int((start_seconds - int(start_seconds)) * 1000)

        end = start + duration
        end_hours, end_remainder = divmod(end, 3600)
        end_minutes, end_seconds = divmod(end_remainder, 60)
        end_milliseconds = int((end_seconds - int(end_seconds)) * 1000)

        srt_content.append(f"{i + 1}")
        srt_content.append(
            f"{int(start_hours):02}:{int(start_minutes):02}:{int(start_seconds):02},{start_milliseconds:03} --> {int(end_hours):02}:{int(end_minutes):02}:{int(end_seconds):02},{end_milliseconds:03}")
        srt_content.append(text)
        srt_content.append('')

    # Ensure the output directory exists
    os.makedirs(srt_save_path, exist_ok=True)

    with open(os.path.join(srt_save_path, 'subtitles.srt'), 'w', encoding='utf-8') as file:
        file.write('\n'.join(srt_content))


def yt_vid_id_to_txt(yt_video_id, txt_save_path):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(txt_save_path), exist_ok=True)

    # Fetch the transcript
    transcript = YouTubeTranscriptApi.get_transcript(yt_video_id)

    # Write the transcript to a .txt file as a single line
    with open(os.path.join(txt_save_path, 'transcript.txt'), 'w', encoding='utf-8') as f:
        full_transcript = ' '.join(entry['text'] for entry in transcript)
        f.write(full_transcript)


def main(yt_vid_url, mp4_dir_save_path, srt_dir_save_path, txt_dir_save_path):
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    yt_video_id = extract_video_id(yt_vid_url)
    yt_vid_id_to_srt(yt_video_id, srt_dir_save_path)
    yt_vid_id_to_txt(yt_video_id, txt_dir_save_path)

if __name__ == "__main__":
    yt_vid_url = input("Enter the YouTube URL: ")
    yt_video_id = extract_video_id(yt_vid_url)
    mp4_dir_save_path = "./input_files"
    srt_dir_save_path = "./whisper_output"
    txt_dir_save_path = "./whisper_output"
    main(yt_vid_url, mp4_dir_save_path, srt_dir_save_path, txt_dir_save_path)
