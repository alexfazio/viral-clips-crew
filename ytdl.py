from pytube import YouTube
from pathlib import Path
import xml.etree.ElementTree as ElementTree
from datetime import timedelta
import os


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

    # Download subtitles if available
    download_subtitles(yt, filename)

    return str(video_file)


def download_subtitles(yt, filename):
    output_dir = Path("./whisper_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    captions = yt.captions
    if captions:
        for lang in captions:
            print(f"Downloading captions for language: {lang.code}")
            xml_captions = captions[lang.code].xml_captions
            srt_captions = xml_caption_to_srt(xml_captions)
            srt_file_path = output_dir / f"{filename}_{lang.code}.srt"
            txt_file_path = output_dir / f"{filename}_{lang.code}.txt"
            
            # Write SRT file
            with open(srt_file_path, 'w', encoding='utf-8') as f:
                f.write(srt_captions)
            
            # Write plain text transcript
            plain_text = srt_to_plain_text(srt_captions)
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
            print(f"Captions saved to {srt_file_path} and {txt_file_path}")
    else:
        print("No captions available for this video.")


def srt_to_plain_text(srt_captions):
    lines = srt_captions.split('\n')
    plain_text_lines = []
    for line in lines:
        if not line.strip().isdigit() and '-->' not in line:
            plain_text_lines.append(line.strip())
    return ' '.join(plain_text_lines).replace('  ', ' ')


def xml_caption_to_srt(xml_captions):
    segments = []
    root = ElementTree.fromstring(xml_captions)
    for i, child in enumerate(root.findall('.//body//p')):
        caption = ''
        if len(list(child)) == 0:
            # simple <p> tag
            caption = child.text or ''
        else:
            # <p> with <s> and <font> children
            for s in list(child):
                if s.tag == 's':
                    caption += (s.text or '') + ' '
                elif s.tag == 'font':
                    caption += (s.text or '') + ' '
        caption = ' '.join(caption.split())  # Normalize spaces
        if not caption:
            continue  # Skip empty captions

        try:
            duration = float(child.attrib["d"]) / 1000.0
        except KeyError:
            duration = 0.0
        start = float(child.attrib.get("t", 0.0)) / 1000.0
        end = start + duration

        sequence_number = len(segments) + 1
        segment = "{0}\n{1} --> {2}\n{3}\n".format(
            sequence_number,
            format_time(start),
            format_time(end),
            caption
        )
        segments.append(segment)
    return "\n".join(segments).strip()


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


if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    save_path = "./input_files"
    print(get_video_from_youtube_url(url, save_path))
