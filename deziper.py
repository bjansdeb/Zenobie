import os
import zipfile

def main():
    path = input("Path :")
    dezip(path)




def dezip(copies_rep):
     for root, dirs, files in os.walk(copies_rep):
        for file in files :
            f = os.path.join(root, file)
            if zipfile.is_zipfile(f):
                with zipfile.ZipFile(f, "r") as zip:
                    zip.extractall(root)



if __name__ == "__main__":
    main()
