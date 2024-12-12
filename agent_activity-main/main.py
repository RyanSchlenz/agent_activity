import subprocess
import os
import time
from project_config import config

def run_script(script_name):
    """Run a Python script using subprocess and return created files."""
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    print(result.stdout)
    
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Retrieve the output files associated with this script from the config
    created_files = config.get('output_files', {}).get(script_name, [])
    return created_files

def delete_files_after_timeout(file_paths, timeout=180):
    """Delete files after a timeout (in seconds)."""
    print(f"Waiting {timeout // 60} minute(s) before deleting files...")
    time.sleep(timeout)  # Wait for the specified timeout (3 minutes = 180 seconds)

    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")

def main():
    # Retrieve the list of scripts from the config file
    scripts = config['scripts']

    # List to hold all created files
    all_created_files = []

    for script in scripts:
        print(f"Running {script}...")
        created_files = run_script(script)
        all_created_files.extend(created_files)

    # Optional: Delete files after a timeout (if necessary)
    delete_files_after_timeout(all_created_files)

if __name__ == "__main__":
    main()
