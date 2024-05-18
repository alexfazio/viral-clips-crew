import os
from send2trash import send2trash

def move_files_to_trash(directory, exclude_files=None):
    """
    Move all files in the specified directory to trash, optionally excluding some files.
    
    :param directory: The directory from which to move files to trash.
    :param exclude_files: A list of filenames to exclude from moving to trash.
    """
    if exclude_files is None:
        exclude_files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename not in exclude_files:
            send2trash(file_path)
            print(f"Moved to trash: {file_path}")

def main():
    clipper_output_dir = 'clipper_output'
    whisper_output_dir = 'whisper_output'
    crew_output_dir = 'crew_output'
    api_response_file = 'api_response.json'

    # Task 1: Move all files in clipper_output to trash
    move_files_to_trash(clipper_output_dir)

    # Task 2: Move all files in whisper_output to trash
    move_files_to_trash(whisper_output_dir)

    # Task 3: Move all files in whisper_output to trash, excluding api_response.json
    move_files_to_trash(whisper_output_dir, exclude_files=[api_response_file])

    # Task 4: Move all files in crew_output to trash, excluding api_response.json
    move_files_to_trash(crew_output_dir, exclude_files=[api_response_file])

if __name__ == "__main__":
    main()
    main()