
import os
import re

def main():
    path = str(input("path : "))
    remove_forbidden_chars(path)


def remove_forbidden_chars(rep):
    #à corriger pour n'obtenir que le nom de fichier sans l'extension, car bugue avec noms de fichier "nom_3.5.5.py"
    pattern = re.compile(r"[\@\]\[\.\^\<\>\:\"\'\{\}\/\|\?\*\x00-\x1F]")
    for root, dirs, files in os.walk(rep):
        for file in files:
            corrected_f =""
            f = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file) 
            if not filename:
                corrected_name = "unnamed"
                corrected_file_n = corrected_name + file_extension
                corrected_f = os.path.join(root, corrected_file_n)
                verify_collision(corrected_f, corrected_name, file_extension, root, f)
            file_lowered = filename.lower()
            if re.search(pattern, file_lowered):
                print(file_lowered, "contains one or more problematic chars")
                corrected_name = pattern.sub("-", file_lowered).replace(" ", "-")
                corrected_file_n = corrected_name + file_extension
                corrected_f = os.path.join(root, corrected_file_n)   
                verify_collision(corrected_f, corrected_name, file_extension, root, f)      



def verify_collision(c_f, c_n, f_e, r, path):
    anti_collision = 0    
    while True:
        if os.path.exists(c_f):
            print(f"attention, {c_f} entraîne une collision")
            anti_collision +=1
            corrected_file_n = c_n +"_" + str(anti_collision) + f_e
            c_f = os.path.join(r, corrected_file_n)
        else:
            break
    try:
        os.rename(path, c_f)
    except FileExistsError:
        raise FileExistsError("The file already exists")
    except PermissionError:
        raise PermissionError("You don't have the permission to rename this file, please retry with running Zenobie with admin right")


if __name__ == "__main__":
    main()