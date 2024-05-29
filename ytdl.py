from pytube import YouTube
from pathlib import Path
import xml.etree.ElementTree as et
import logging


def parse_auto_generated_captions(xml_captions):
    root = et.fromstring(xml_captions)
    srt_captions = []
    for i, child in enumerate(root.findall('.//body/p')):
        text = ''.join(child.itertext()).strip()
        if not text:
            continue
        start = float(child.attrib.get('t', '0')) / 1000.0
        duration = float(child.attrib.get('d', '0')) / 1000.0
        end = start + duration
        srt_captions.append(f"{i + 1}\n{format_time(start)} --> {format_time(end)}\n{text}\n")
    return '\n'.join(srt_captions)


def format_time(seconds):
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def get_video_from_youtube_url(url, save_path=None):
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

    # Fetch and save subtitles if available
    subtitles = yt.captions
    if subtitles:
        # Look for English captions, including auto-generated ones
        caption = subtitles.get('en') or subtitles.get('a.en')
        if not caption:
            # Use the first available caption if English is not found
            caption = next(iter(subtitles.values()))
            logging.warning(f"No English captions available, using {caption.code} instead.")
        else:
            logging.info(f"Using captions in {caption.code}")

        try:
            if caption.code.startswith('a.'):
                # Handle auto-generated captions
                srt_caption = parse_auto_generated_captions(caption.xml_captions)
            else:
                srt_caption = caption.generate_srt_captions()

            subtitle_path = save_path / f"{filename}.srt"
            with open(subtitle_path, 'w') as file:
                file.write(srt_caption)
            logging.info("Subtitles downloaded successfully.")

            # Save transcription as plain text
            transcript_text = "\n".join(
                line.strip() for line in srt_caption.splitlines() if "-->" not in line and line.strip())
            transcript_path = save_path / f"{filename}.txt"
            with open(transcript_path, 'w') as file:
                file.write(transcript_text)
            logging.info("Transcription downloaded successfully.")
        except Exception as e:
            logging.error(f"An error occurred while generating captions: {e}")
    else:
        logging.warning("No subtitles available for this video.")

    return str(video_file)


if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    logging.info(get_video_from_youtube_url(url, "./input_files"))

