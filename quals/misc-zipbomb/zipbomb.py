import os
import zipfile
import random
import string

# --- Configuration ---
INITIAL_FILE = 'flag.txt'
RECURSION_DEPTH = 1000
DUMMY_FILE_SIZE = 1024
FINAL_NAME = "bomb.zip"
# ---------------------

def generate_random_string(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def create_dummy_file(filename, size):
    try:
        with open(filename, 'wb') as f:
            f.write(b"DOWNLOAD MORE RAM "*size)
    except IOError as e:
        print(f"Error creating dummy file {filename}: {e}")
        raise

def create_zip(zip_name, files_to_add):
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in files_to_add:
                if os.path.exists(file):
                    zf.write(file, os.path.basename(file))
                else:
                    print(f"Warning: File {file} not found, skipping.")
    except IOError as e:
        print(f"Error creating zip file {zip_name}: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

def main():    
    if not os.path.exists(INITIAL_FILE):
        print(f"{INITIAL_FILE} not found. Creating a dummy one.")
        try:
            with open(INITIAL_FILE, 'w') as f:
                f.write('This is a dummy flag. The real one was not found.')
        except IOError as e:
            print(f"Fatal: Could not create {INITIAL_FILE}: {e}")
            return

    print(f"Starting recursive zipping for '{INITIAL_FILE}'...\n")

    try:
        first_zip_name = generate_random_string() + '.zip'
        create_zip(first_zip_name, [INITIAL_FILE])
        print(f"Step 0: Zipped '{INITIAL_FILE}' into '{first_zip_name}'")
        
        previous_zip_name = first_zip_name

        for i in range(1, RECURSION_DEPTH + 1):
            dummy_file_name = generate_random_string() + '.txt'
            create_dummy_file(dummy_file_name, DUMMY_FILE_SIZE)
            
            new_zip_name = generate_random_string() + '.zip' if i != RECURSION_DEPTH else FINAL_NAME
            files_to_zip = [previous_zip_name, dummy_file_name]
            create_zip(new_zip_name, files_to_zip)
            
            print(f"Step {i}: Zipped '{previous_zip_name}' and '{dummy_file_name}' into '{new_zip_name}'")

            os.remove(previous_zip_name)
            os.remove(dummy_file_name)
            
            previous_zip_name = new_zip_name

        print(f"\nProcess complete. The final file is: {previous_zip_name}")
        assert previous_zip_name == FINAL_NAME

    except Exception as e:
        print(f"\nAn error occurred during the process: {e}")
        print("Cleaning up any remaining intermediate files...")
        if 'dummy_file_name' in locals() and os.path.exists(dummy_file_name):
            os.remove(dummy_file_name)
        if 'previous_zip_name' in locals() and os.path.exists(previous_zip_name) and previous_zip_name != first_zip_name:
             pass
        if 'first_zip_name' in locals() and os.path.exists(first_zip_name) and 'previous_zip_name' in locals() and first_zip_name != previous_zip_name:
            os.remove(first_zip_name)


if __name__ == "__main__":
    main()