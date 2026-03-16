
import os
import re

FORBIDDEN_CHARS = re.compile(r"[\@\]\[\^\<\>\:\"\'\{\}\/\|\?\*\x00-\x1F]")

def main():
    path = str(input("path : "))
    remove_forbidden_chars(path)


def remove_forbidden_chars(rep):
    for root, dirs, files in os.walk(rep):
        for file in files:
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file) 
            if not filename:
                filename = "unnamed"

            if re.search(FORBIDDEN_CHARS, filename):
                filename = FORBIDDEN_CHARS.sub("-", filename)
            
            filename = filename.replace(" .", ".")
            filename = filename.replace(" ", "_")
            new_filename = filename + file_extension
            new_path = os.path.join(root, new_filename)
            if new_path == old_path:
                continue

            normalized_name = verify_collision(new_path)      
            try:
                os.rename(old_path, normalized_name)
            except FileExistsError:
                raise FileExistsError("There is a collision between two files names")
            except PermissionError:
                raise PermissionError("You don't have the permission to modify the file, please run Zenobie again with ")
            except OSError as e:
                raise OSError(f"Zenobie failed to rename {old_path}: {e}")

def verify_collision(n_path):
    base, ext = os.path.splitext(n_path)
    counter = 0
    candidate = n_path
    while os.path.exists(candidate):
            counter +=1
            candidate = f"{base}_{counter}{ext}"
    return candidate

if __name__ == "__main__":
    main()