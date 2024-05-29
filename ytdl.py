from pytube import YouTube
from pathlib import Path


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

    return str(video_file)


if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    save_path = "./input_files"
    print(get_video_from_youtube_url(url, save_path))
