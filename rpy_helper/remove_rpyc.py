import os

def remove_rpyc_files(directory: str):
    """Removes all .rpyc files from the given directory and its subdirectories."""
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".rpyc"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    print(f"Total .rpyc files removed: {count}")


dir = "C:\Codes\RPY\VN_HerWitch"
remove_rpyc_files(dir)