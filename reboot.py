import os
from send2trash import send2trash

def move_files_to_trash(directory, exclude_files=None):
    """
    Move all files and directories in the specified directory to trash, optionally excluding some files.
    
    :param directory: The directory from which to move files and directories to trash.
    :param exclude_files: A list of filenames to exclude from moving to trash.
    """
    if exclude_files is None:
        exclude_files = []

    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename not in exclude_files:
            send2trash(file_path)
            print(f"Moved to trash: {file_path}")

    # Move the directory itself to trash
    send2trash(directory)
    print(f"Moved to trash: {directory}")

def clear_file_contents(file_path):
    """
    Clear the contents of the specified file.
    
    :param file_path: The path to the file to clear.
    """
    with open(file_path, 'w') as file:
        file.write('')
    print(f"Cleared contents of file: {file_path}")

def main():
    clipper_output_dir = 'clipper_output'
    whisper_output_dir = 'whisper_output'
    crew_output_dir = 'crew_output'
    api_response_file = 'api_response.json'

    # Task 1: Move all files and the directory clipper_output to trash
    move_files_to_trash(clipper_output_dir)

    # Task 2: Move all files and the directory whisper_output to trash
    move_files_to_trash(whisper_output_dir)

    # Task 3: Move all files in crew_output to trash, excluding api_response.json, but do not move the directory itself
    for filename in os.listdir(crew_output_dir):
        file_path = os.path.join(crew_output_dir, filename)
        if filename != api_response_file:
            send2trash(file_path)
            print(f"Moved to trash: {file_path}")

    # Clear the contents of api_response.json
    clear_file_contents(os.path.join(crew_output_dir, api_response_file))

if __name__ == "__main__":
    main()
    main()