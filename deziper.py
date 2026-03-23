import os
import py7zr
import tarfile
import zipfile
import logging
import typing 
from pathlib import Path


MAX_FILES = 1_000
MAX_TOTAL_SIZE = 1_000_000_000
AUTHORIZED_PACKS = {".zip", ".tar", ".7z"}
UNAUTHORIZED_PACKS = {".rar"}


def main():
    path = input("Path :")
    dezip(path)


def dezip(copies_rep):
    exceeding_packs = []
    uncompliant_packs = []
    for root, dirs, files in os.walk(copies_rep):
        for file in files :
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(old_path)

            if file_extension.lower() in UNAUTHORIZED_PACKS:
                uncompliant_packs.append(old_path)
                continue
            if file_extension.lower() not in AUTHORIZED_PACKS:
                """let the other files formats which are not packs"""
                continue


            new_path = filename

            if os.path.isdir(filename):
                new_path = verify_collision(filename)
            os.mkdir(new_path)
            logging.info(f"New reposit created during dezip process {new_path}")


            match file_extension:
                case ".zip":
                    extract_zipfile(old_path, new_path, uncompliant_packs, exceeding_packs)
                case ".tar":
                    extact_tarfile(old_path, new_path, uncompliant_packs, exceeding_packs)
                case ".gz":
                    extact_tarfile(old_path, new_path, uncompliant_packs, exceeding_packs)
                case ".7z":
                    extract_7zfile(old_path, new_path, uncompliant_packs, exceeding_packs)

    if uncompliant_packs :
        pat = "uncompliant_packs.txt"
        with open(pat, "w+t", encoding="utf-8") as uncompliant_r:
            uncompliant_r.write("Uncompliant packs :")
            for pack in exceeding_packs:
                uncompliant_r.write(f"\n{pack}")

        logging.info(f"There are packages not compliant with your format policy.")
        logging.info(f"You can check the list here : {pat}")
        logging.info(f"Please, note that some of these packs may contain dangerous links")
        answeer= input("May I remove them (yes/no)? :")
        while True :
            if answeer == "yes":
                for pack in uncompliant_packs:
                    remove_pack(pack)
                break
            elif answeer == "no":
                break
    else:
        pass

    if exceeding_packs:
        pat = "exceeding_packs.txt"
        with open(pat, "w+t", encoding="utf-8") as uncompliant_r:
            uncompliant_r.write("Exceeding packs :")
            for pack in exceeding_packs:
                uncompliant_r.write(f"\n{pack}")


        logging.info(f"There are also packages compliant with your format policy but that exceeds the authorized maximum size of 1 go or maximum number of files")
        logging.info(f"You can check the list here : {pat}")
        anwseer = input("May I remove them (yes/no)? :")
        while True:
            if anwseer == "yes":
                for pack in exceeding_packs:
                    remove_pack(pack)
                break
            elif answeer == "no":
                break


def extract_zipfile(old_path, new_path, uncomp_pack, exceed_pack): 
    with zipfile.ZipFile(old_path, "r") as zip:
        compressed_size = 0
        files_number = 0
        for entry in zip.infolist():
            if not entry.is_dir():
                compressed_size += entry.file_size
                files_number +=1
            if not is_safe_path(old_path, entry.filename):
                uncomp_pack.append(old_path)
                return
            
            if os.path.is_link(entry):
                uncomp_pack.append(old_path)
                return
            
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            logging.warning(f"{old_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            exceed_pack.append(old_path)
            return

        zip.extractall(new_path)
        logging.info(f"{old_path} extracted")
    remove_pack(old_path)

def extact_tarfile(old_path, new_path, uncomp_pack, exceed_pack):
    with tarfile.open(old_path, "r:*") as tar:
        compressed_size = 0
        files_number= 0
        members = tar.getmembers()
        for entry in members:
            if not entry.isdir():
                compressed_size += entry.size
                files_number +=1

            if not is_safe_path(old_path, entry.name):
                uncomp_pack.append(old_path)
                return
            
            if entry.issym() or entry.islnk:
                #against symlink attacks https://www.tencentcloud.com/techpedia/124101
                uncomp_pack.append(old_path)
                return
            
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            logging.warning(f"{new_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            exceed_pack.append(old_path)
            return
        
        tar.extractall(new_path, filter="data")       
        logging.info(f"{old_path} extracted")            
    remove_pack(old_path)


def extract_7zfile(old_path, new_path, exceed_pack):
    with py7zr.SevenZipFile(old_path, 'r') as z:
        compressed_size = 0
        files_number = 0
        members = z.list()
        infos_package = z.archiveinfo()

        for entry in members:
            if entry.is_file :
                files_number +=1

            if not is_safe_path(old_path, entry.filename):
                return

            if entry.is_symlink:
                return        
        compressed_size = infos_package.uncompressed
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            logging.warning(f"{new_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            exceed_pack.append(old_path)
            return
        
        z.extractall(new_path)
        logging.info(f"{old_path} extracted")
    remove_pack(old_path)


def remove_pack(old_path):
    os.remove(old_path)  
    logging.info(f"{old_path} was removed")              

def verify_collision(n_path):
    base, ext = os.path.splitext(n_path)
    counter = 0
    candidate = n_path
    while os.path.exists(candidate):
            counter +=1
            candidate = f"{base}_{counter}{ext}"
    return candidate

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
