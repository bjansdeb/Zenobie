import datetime
import hashlib
import os
import subprocess
import shutil
import sys

def main():
    user = str(input("Who are you : "))
    repository = str(input(f"Hello {user}. What's the repository of the vrac archives : "))
    print("you have indicated :", repository)
    if os.path.isdir(repository):
        sail_to_bay(repository, user)
        state_of_art(repository, user)
        dezip()
        droid_check()
        remove_empty()        
    else :
        print("Path not correct, retry please")
        pass



"""Création et transfert vers la baie d'embarquement avec calcul hash"""
def sail_to_bay(rep, us):
    directory = "unload_bay"
    parent_dir = os.path.dirname(__file__)
    path = os.path.join(parent_dir, directory)
    """Création du rapport"""
    transfert_report = open("transfert_report.txt", "w+t")

    """Création de la baie si inexistante"""
    if os.path.isdir(path):
         print("Unload bay already exists")       
    else : 
        os.mkdir(path)

    original_rep = "original_room"
    copies_rep = "sorting_room"
    originals = os.path.join(path, original_rep)
    if os.path.isdir(originals):
        print("Originals repository already exists")
    else :
        os.mkdir(originals)

    copies = os.path.join(path, copies_rep)

    if os.path.isdir(copies):
        print("Copies repository already exists")
        robotcopy = subprocess.run(["robocopy", rep, copies, "/e", "/copyall", f"/log+:{parent_dir}/transfert_report.txt"], check=False)
        print(robotcopy)
    else :
        os.mkdir(copies)
    #faire en sorte de copier les fichiers vers original and copied files
 

    #calculer le hash de base pour les trois dossiers 
    """Calcul du checksum original avant transfert"""
    hash_calculator(rep)
    original_items =""
    copied_items= ""
    """Vérification du checksum après transfert"""
    hash_calculator(original_items)
    hash_calculator(copied_items)

    date = horodatage() #horodatage du rapport
    transfert_report.write(f"Transfert done by {us} at {date}")
    transfert_report.write(f"\nHash of the original files : {hash}")
    transfert_report.close()

"""Etat des lieux"""
def state_of_art(rep, us):
    start_depth = 1
    state_report = open("state_report.txt", "w+t")
    full_size = str(os.path.getsize(str(rep))) #taille du contenu de la totalité du répertoire en bytes
    date = horodatage() #horodatage du rapport
    stats = os.stat(rep)
    for root, dirs, files in os.walk(rep):
        current_depth = root.replace(rep, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = max(start_depth, current_depth) #calcule la différence entre le niveau 1 et le compte des profondeurs

    # print(f"Audit of {rep}")
    # print("Size of the repository", full_size + " bytes")    
    # print("Max-depth:", max_depth)
    # print("Stats:", stats)
    # print(f"Report done with Zenobie at {date}")
    state_report.write(f"Audit of {rep}")
    state_report.write(f"\nSize of the repository" + full_size + " bytes")
    state_report.write(f"\nMax-depth: {max_depth}")
    state_report.write(f"\nStats : {stats}")
    state_report.write(f"\nReport done with Zenobie at {date} by {us}")

"""Décompression des fichiers"""
def dezip():
    ...

def droid_check():
    ...
"""Suppression de dossiers vides"""
def remove_empty():
    ...

def hash_calculator(item): 
    sha_256 = hashlib.sha256(b"item") #à retravailler car calculte le hash sur "item" et non la variable
    md5 = hashlib.md5(b"item")
    # print("sha_256", sha_256, "md5", md5)
    return sha_256, md5

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

if __name__ == "__main__":
    main()