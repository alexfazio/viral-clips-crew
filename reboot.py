import os
from send2trash import send2trash
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def move_files_to_trash(directory, exclude_files=None, file_extension=None):
    """
    Move files in the specified directory to trash, optionally excluding some files and filtering by extension.
    
    :param directory: The directory from which to move files to trash.
    :param exclude_files: A list of filenames to exclude from moving to trash.
    :param file_extension: If provided, only files with this extension will be moved to trash.
    """
    if exclude_files is None:
        exclude_files = []

    if not os.path.exists(directory):
        logging.error(f"Directory not found: {directory}")
        return

    for filename in os.listdir(directory):
        if filename not in exclude_files:
            if file_extension is None or filename.lower().endswith(file_extension.lower()):
                file_path = os.path.join(directory, filename)
                send2trash(file_path)
                logging.info(f"Moved to trash: {file_path}")

def clear_file_contents(file_path):
    """
    Clear the contents of the specified file.
    
    :param file_path: The path to the file to clear.
    """
    with open(file_path, 'w') as file:
        file.write('')
    logging.info(f"Cleared contents of file: {file_path}")

def main():
    print("WARNING: Running reboot.py will erase both input and output files!")
    user_input = input("Are you sure you want to continue? (y/n): ")
    if user_input.lower() != 'y':
        print("Operation cancelled.")
        return

    clipper_output_dir = 'clipper_output'
    whisper_output_dir = 'whisper_output'
    crew_output_dir = 'crew_output'
    input_files_dir = 'input_files'
    subtitler_output_dir = 'subtitler_output'
    api_response_file = 'api_response.json'

    # Task 1: Move all files and the directory clipper_output to trash
    move_files_to_trash(clipper_output_dir)

    # Task 2: Move all .mp4 files in clipper_output to trash
    move_files_to_trash(clipper_output_dir, file_extension='.mp4')

    # Task 3: Move all files and the directory whisper_output to trash
    move_files_to_trash(whisper_output_dir)

    # Task 4: Move all files in crew_output to trash, excluding api_response.json, but do not move the directory itself
    move_files_to_trash(crew_output_dir, exclude_files=[api_response_file])

    # Task 5: Move all mp4 files in input_files to trash, excluding PLACE_CLIPS_HERE
    move_files_to_trash(input_files_dir, exclude_files=['PLACE_CLIPS_HERE'], file_extension='.mp4')

    # Task 6: Move all mp4 files in subtitler_output to trash if the directory exists
    if os.path.exists(subtitler_output_dir):
        move_files_to_trash(subtitler_output_dir, file_extension='.mp4')

    # Clear the contents of api_response.json
    clear_file_contents(os.path.join(crew_output_dir, api_response_file))

if __name__ == "__main__":
    main()