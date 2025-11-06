import datetime, hashlib, os, subprocess, shutil, sys
import csv
from zenoclasses import Agent, Action, Report

def main():
    print("Welcome, my name is Zenobie and I'm going to help you to deal your digital bulk")
    name = str(input("What's your name : "))
    role = str(input(f"Hello {name}. What's your role at Carhif: "))
    user = Agent ("0001",name, role, "individual", "AVG-CARHIF", "")
    repository, originals_repository, copies_repository = "", "", ""
    # report = Report() 
    while True:
        try:
            repository = str(input("Super ! Ok let's work, what's the path to your digital bulk repository :"))
            break
        except IsADirectoryError:
            raise("Repertory nod valid, retry with a correct path name")        
        except:
            raise ValueError("Repertory not valid, retry") 

               

    originals_repository, copies_repository = create_bay(user)      
    if os.path.isdir(repository):
        copies_repository = sail_to_bay(repository, originals_repository, copies_repository, user) #la fonction retourne le répertoire des copies sur lequel va se faire le state of art
    if os.path.isdir(copies_repository):
        state_of_art(repository, user.name)
        while True:
            try:
                answeer = str(input("Do we remove empty repositories ? (type yes or no)")).lstrip().lower()
                if answeer == "yes":
                    dezip()
                elif answeer == "no":
                    print("ok, we continue without dezipping repositories")
                    break            
            except:
                raise ValueError("Please, answeer yes or no")
        droid_check()
        remove_empty()
        print(f"Process finished, bye {user.name}")        
    else :
        print("Path not correct, retry please")
        pass

"""-----------------------------------------------"""
"""Functions"""
"""-----------------------------------------------"""

"""Création et transfert vers la baie d'embarquement avec calcul hash"""

def create_bay(rep, user):
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
    else :
        os.mkdir(copies)
    
    return originals, copies

def sail_to_bay(rep, user):
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
        csvfile = open('hash_report.csv', 'w', newline='', encoding='utf-8') #à corriger
        hash_report = csv.writer(csvfile)
        for root, dir, files in os.walk(rep): 
            for file in files :
                f =os.path.join(root, file)
                md5 = hash_calculator(f)
                hash_report.writerow([f])
                hash_report.writerow([md5])
        robot_copy(rep, originals, parent_dir)

        hash_report.writerow([user.name])
        # hash_calculator(originals)
    else :
        os.mkdir(originals)

    copies = os.path.join(path, copies_rep)

    if os.path.isdir(copies):
        print("Copies repository already exists")
        robot_copy(rep, copies, parent_dir)
    else :
        os.mkdir(copies)
    
    return copies
    #faire en sorte de copier les fichiers vers original and copied files
 

    #calculer le hash de base pour les trois dossiers 
    """Calcul du checksum original avant transfert"""
    # hash_calculator(rep)
    # original_items =""
    # copied_items= ""
    # """Vérification du checksum après transfert"""
    # hash_calculator(original_items)
    # hash_calculator(copied_items)

    # date = horodatage() #horodatage du rapport
    # transfert_report.write(f"Transfert done by {us} at {date}")
    # transfert_report.write(f"\nHash of the original files : {hash}")
    # transfert_report.close()

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
    print("dezip done")

def droid_check():
    print("time to droid check")
    ...
"""Suppression de dossiers vides"""
def remove_empty():
    ...

def robot_copy(source, destination, log_repository):
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    robotcopy = subprocess.run(["robocopy", source, destination, "/e", "/copyall", f"/log+:{log_repository}/transfert_report.txt"], check=False)
    #robotcopy contient de nombreuses métadonnées qu'on pourrait utiliser pour le rapport ultérieurement

def hash_calculator(source):
    # sha_256 = hashlib.sha256() #à décocher si on veut cet algo à la place de md5
    md5 = hashlib.md5()
    print(source)
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

if __name__ == "__main__":
    main()