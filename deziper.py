import os
import tarfile
import zipfile
import logging
from typing import Path

MAX_FILES = 10_000
MAX_TOTAL_SIZE = 1_000_000_000
AUTHORIZED_ZIP = {".zip", ".tar", ".rar", ".7z"}

def main():
    path = input("Path :")
    dezip(path)


def dezip(copies_rep):
     for root, dirs, files in os.walk(copies_rep):
        for file in files :
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(old_path)
            if file_extension.lower() not in AUTHORIZED_ZIP:
                continue
            new_path = old_path    
            if os.path.isdir(filename):
                new_path = verify_collision(filename)
                print("new reposit created")

            os.mkdir(new_path)
            print(f"{new_path}  ")            
            match file_extension:
                case ".zip":
                    extract_zipfile(old_path, new_path)
                case ".tar":
                    extact_tarfile(old_path, new_path)
                case ".gz":
                    extact_tarfile(old_path, new_path)
                case ".rar":
                    ...
                case ".7z":
                    ...

def extract_zipfile(old_path, new_path): 
    with zipfile.ZipFile(old_path, "r") as zip:
        compressed_size = 0
        files_number = 0
        for entry in zip.infolist():
            if not entry.is_dir():
                compressed_size += entry.file_size
                files_number +=1    
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            logging.warning(f"{new_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            answeer = input(
                "This compressed file exceeds the authorized limits and can endanger your system. " \
                "Do you want continue ? If no, Zenobie will simply skip the problematic compressed file")
            if answeer == "yes":
                ...#break
            elif answeer=="no":
                ...#continue
        zip.extractall(new_path)
        logging.info(f"{new_path} extracted")

def extact_tarfile(old_path, new_path):
    with tarfile.open(old_path, 'r') as tar:
        compressed_size = 0
        files_number= 0
        members = tar.getmembers()
        for entry in members:
            if not entry.is_dir():
                compressed_size += entry.file_size
                files_number +=1
            if not is_safe_path(entry):
                return
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            logging.warning(f"{new_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            answeer = input(
                "This compressed file exceeds the authorized limits and can endanger your system. " \
                "Do you want continue ? If no, Zenobie will simply skip the problematic compressed file")
            if answeer == "yes":
                ...#break
            elif answeer=="no":
                ...#continue 
        tar.extractall(new_path, filter="data")                   
                

def verify_collision(n_path):
    base, ext = os.path.splitext(n_path)
    counter = 0
    candidate = n_path
    while os.path.exists(candidate):
            counter +=1
            candidate = f"{base}_{counter}{ext}"
    return candidate

def is_safe_path(path_content):
     ...
def is_safe_path(base_dir: Path, requested_path: str) -> bool:
    #https://medium.com/@contactomyna/securing-zip-file-operations-understanding-and-preventing-path-traversal-attacks-74d79f696c46
    """Ensure file operations occur within the intended directory"""
    try:
       base_dir = Path(base_dir).resolve()
       target_path = Path(base_dir, requested_path).resolve()
       return target_path.is_relative_to(base_dir)
    except (RuntimeError, ValueError):
       return False

if __name__ == "__main__":
    main()
