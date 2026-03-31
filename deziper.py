import os
import py7zr
import stat
import tarfile
import zipfile

from log import log_it
from pathlib import Path
from config import read_config

config_data = read_config()

MAX_FILES = int(config_data['max_files'])
MAX_TOTAL_SIZE = int(config_data['max_total_size'])
AUTHORIZED_PACKS = config_data['authorized_packs']
UNAUTHORIZED_PACKS = config_data['unauthorized_packs']


def main():
    path = input("Path :")
    dezip(path)


def dezip(copies_rep):
    """
    Docstring for dezp
    Fonction de décompression
    :param copies_rep: path : attention, ne prend que des répertoires, pas des fichiers
    """

    exceeding_packs = []
    uncompliant_packs = []
    archives_to_unpack = []
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
            archives_to_unpack.append((old_path, filename, file_extension.lower()))
    
    for old_path, filename, file_extension in archives_to_unpack:
        match file_extension:
            case ".zip":
                extract_zipfile(old_path, filename, uncompliant_packs, exceeding_packs)
            case ".tar":
                extract_tarfile(old_path, filename, uncompliant_packs, exceeding_packs)
            case ".gz":
                extract_tarfile(old_path, filename, uncompliant_packs, exceeding_packs)
            case ".7z":
                extract_7zfile(old_path, filename, uncompliant_packs, exceeding_packs)

    if uncompliant_packs :
        pat = "uncompliant_packs.txt"
        with open(pat, "w+t", encoding="utf-8") as uncompliant_r:
            uncompliant_r.write("Uncompliant packs :")
            for pack in uncompliant_packs:
                uncompliant_r.write(f"\n{pack}")

        log_it("info", f"There are packages not compliant with your format policy.")
        log_it("info",f"You can check the list here : {pat}")
        log_it("info",f"Please, note that some of these packs may contain dangerous links")
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


        log_it("info", f"There are also packages compliant with your format policy but that exceeds the authorized maximum size of 1 go or maximum number of files")
        log_it("info",f"You can check the list here : {pat}")
        anwseer = input("May I remove them (yes/no)? :")
        while True:
            if anwseer == "yes":
                for pack in exceeding_packs:
                    remove_pack(pack)
                break
            elif answeer == "no":
                break


def extract_zipfile(old_path, file_n, uncomp_pack, exceed_pack): 
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
            
            """Détecte les symlinks en bas niveau, Python 3.11.19 n'offre pas de fonction pour ça avec zipfile"""
            mode = entry.external_attr >> 16
            print(mode)
            
            if stat.S_ISLNK(mode):
                uncomp_pack.append(old_path)
                return
            print("external attributes", entry.external_attr)
            
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            log_it("warning",f"{old_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            exceed_pack.append(old_path)
            return

        new_path = file_n

        if os.path.isdir(file_n):
            new_path = verify_collision(file_n)
        os.mkdir(new_path)
        log_it("info",f"New reposit created during dezip process {new_path}")

        zip.extractall(new_path)
        log_it("info", f"{old_path} extracted")
    remove_pack(old_path)

def extract_tarfile(old_path, file_n, uncomp_pack, exceed_pack):
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
            log_it("warning",f"{old_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            exceed_pack.append(old_path)
            return

        new_path = file_n

        if os.path.isdir(file_n):
            new_path = verify_collision(file_n)
        os.mkdir(new_path)

        log_it("info",f"New reposit created during dezip process {new_path}")
        
        tar.extractall(new_path, filter="data")       
        log_it("info",f"{old_path} extracted")            
    remove_pack(old_path)


def extract_7zfile(old_path, file_n, uncomp_pack, exceed_pack):
    with py7zr.SevenZipFile(old_path, 'r') as z:
        compressed_size = 0
        files_number = 0
        members = z.list()
        infos_package = z.archiveinfo()

        for entry in members:
            if entry.is_file :
                files_number +=1

            if not is_safe_path(old_path, entry.filename):
                uncomp_pack.append(old_path)
                return

            if entry.is_symlink:
                uncomp_pack.append(old_path)
                return
                    
        compressed_size = infos_package.uncompressed
        if compressed_size >= MAX_TOTAL_SIZE or files_number >= MAX_FILES:
            log_it("warning",f"{old_path} has a size above the limits with  {compressed_size} bytes, {files_number}")
            exceed_pack.append(old_path)
            return
        
        new_path = file_n
        print(old_path)
        if os.path.isdir(file_n):
            new_path = verify_collision(file_n)
        os.mkdir(new_path)

        log_it("info",f"New reposit created during dezip process {new_path}")
        print(old_path)       
        z.extractall(path=new_path)

        log_it("info",f"{old_path} extracted")
    remove_pack(old_path)


def remove_pack(old_path):
    os.remove(old_path)  
    log_it("info",f"{old_path} was removed")              

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
