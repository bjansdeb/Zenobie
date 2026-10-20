
import os
import re

from pathlib import Path

FORBIDDEN_CHARS = re.compile(r"[\@\]\[\^\<\>\:\"\'\{\}\/\|\?\*\x00-\x1F]")


def main():
    path = str(input("path : "))
    remove_forbidden_chars(path)


def remove_forbidden_chars(repository_path):
    for root, _, files in os.walk(repository_path):
        for file in files:
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file)
            old_name = get_relative_path(old_path, repository_path) 
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

            normalized_path = verify_collision(new_path)      
            try:
                os.rename(old_path, normalized_path)
                new_name = get_relative_path(normalized_path, repository_path)
                print(fr"Original name: {old_name} - New name: {new_name}")
            except FileExistsError:
                raise FileExistsError("There is a collision between two files names")
            except PermissionError:
                raise PermissionError("You don't have the permission to modify the file, please run Zenobie again with the admin privileges")
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

def get_relative_path(child_path: str, absolute_parent_path: str) -> str:
    """Calcule le chemin relatif pour un chemin individuel donné à partir du répertoire parent absolu"""
    child = Path(child_path)
    parent = Path(fr'{absolute_parent_path}')
    path = str(parent.name / child.relative_to(parent)) #.as_posix()
    return path #.as_posix()

if __name__ == "__main__":
    main()