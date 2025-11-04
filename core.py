import os
import sys
import datetime
import hashlib

def main():
    user = str(input("Who are you : "))
    repository = str(input(f"Hello {user}. What's the repository of the vrac archives : "))
    print("you have indicated :", repository)
    if os.path.isdir(repository):
        sail_to_bay(repository, user)
        state_of_art(repository, user)
        dezip()
        remove_empty()        
    else :
        print("Path not correct, retry please")
        pass



"""Création et transfert vers la baie d'embarquement"""
def sail_to_bay(rep, us):
    directory = "unload_bay"
    parent_dir = os.path.dirname(__file__)
    path = os.path.join(parent_dir, directory)
    if os.path.isdir(path):
         print("Unload bay already exists")       
    else : 
        os.mkdir(path)

    original_rep = "original_files"
    copies_rep = "copied_files"
    originals = os.path.join(path, original_rep)
    if os.path.isdir(originals):
        print("Originals repository already exists")
    else :
        os.mkdir(originals)

    copies = os.path.join(path, copies_rep)

    if os.path.isdir(copies):
        print("Copies repository already exists")
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

    date = datetime.datetime.now() #horodatage du rapport
    transfert_report = open("transfert_report.txt", "w+t")
    transfert_report.write(f"Transfert done by {us} at {date}")
    transfert_report.write(f"\nHash of the original files : {hash}")
    transfert_report.close()

"""Etat des lieux"""
def state_of_art(rep, us):
    start_depth = 1
    count = 0
    state_report = open("state_report.txt", "w+t")
    full_size = str(os.path.getsize(str(rep))) #taille du contenu de la totalité du répertoire en bytes
    date = datetime.datetime.now() #horodatage du rapport
    stats = os.stat(rep)
    for root, dirs, files in os.walk(rep):
        current_depth = root.replace(rep, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = max(start_depth, current_depth) #calcule la différence entre le niveau 1 et le compte des profondeurs

    print(f"Audit of {rep}")
    print("Size of the repository", full_size + " bytes")    
    print("Max-depth:", max_depth)
    print("Stats:", stats)
    print(f"Report done with Zenobie at {date}")
    state_report.write(f"Audit of {rep}")
    state_report.write(f"\nSize of the repository" + full_size + " bytes")
    state_report.write(f"\nMax-depth: {max_depth}")
    state_report.write(f"\nStats : {stats}")
    state_report.write(f"\nReport done with Zenobie at {date} by {us}")

"""Décompression des fichiers"""
def dezip():
    ...

"""Suppression de dossiers vides"""
def remove_empty():
    ...

def hash_calculator(item):
    sha_256 = hashlib.sha256(b"item")
    md5 = hashlib.md5(b"item")
    print("sha_256", sha_256, "md5", md5)
    return sha_256, md5

if __name__ == "__main__":
    main()