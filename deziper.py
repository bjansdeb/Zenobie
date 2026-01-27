import os
import zipfile

MAX_FILES = 10_000
MAX_TOTAL_SIZE = 1_000_000_000
AUTHORIZED_ZIP = {".zip", ".tar"}

def main():
    path = input("Path :")
    dezip(path)


def dezip(copies_rep):
     for root, dirs, files in os.walk(copies_rep):
        for file in files :
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(old_path)
            if not zipfile.is_zipfile(old_path):
                continue
            if file_extension.lower() not in AUTHORIZED_ZIP:
                continue
            
            new_path = old_path    
            if os.path.isdir(filename):
                new_path = verify_collision(filename)
                print("new reposit created")
            else :
                os.mkdir(new_path)
                print(f"{new_path}  ")

            with zipfile.ZipFile(old_path, "r") as zip:
                zip.extractall(root)


                

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
