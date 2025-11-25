import csv 
import datetime 
import hashlib
import os 
import subprocess
import shutil
import sys
import zipfile

from zenoclasses import Agent, Event, Object, Report, Mets, State

#os.utime() report
mets = Mets(1, "2020","2021", "Benjamin", 15)


def main():
    print("Welcome, my name is Zenobie and I'm going to help you to deal your digital bulk")
    name = str(input("What's your name : "))
    role = str(input(f"Hello {name}. What's your role at Carhif: "))
    user = Agent (name, "local", agentType=None, note=role)
    repository, originals_repository, copies_repository, project_name  = "", "", "", ""
    while True:
        try:
            repository = str(input("Super ! Ok let's work, what's the path to your digital bulk repository :"))
            project_name = os.path.basename(repository)
            break
        except IsADirectoryError:
            raise("Repertory nod valid, retry with a correct path name")        
        except NotADirectoryError: 
            raise("Please select a directory and retry")
        except ValueError:
            raise ("Repertory not valid, retry") 


               

    originals_repository, copies_repository, unload_bay, reports = create_bay(user, project_name)  #création des dossiers de la baie d'arrivage si n'existent pas    
    if os.path.isdir(repository):
        sail_to_bay(repository, originals_repository, 
                    copies_repository, unload_bay, reports, user) #la fonction retourne le répertoire des copies sur lequel va se faire le state of art
    if os.path.isdir(copies_repository):
        state_of_art(repository, reports, user)
        while True:
            try:
                answeer = str(input("May I remove empty repositories(yes or no)?")).lstrip().lower()
                if answeer == "yes":
                    dezip(copies_repository)
                    break
                elif answeer == "no":
                    print("ok, we continue without dezipping repositories")
                    break            
            except ValueError:
                print("Please, answeer yes or no")
                pass
        remove_empty(copies_repository)
        droid_check()

        print(f"Process finished, bye {user.agentName}")        
    else :
        print("Path not correct, retry please")
        pass

"""-----------------------------------------------"""
"""            **** Functions   ****"""
"""-----------------------------------------------"""

"""Création et transfert vers la baie d'embarquement avec calcul hash"""

def create_bay(user, project_n):
    parent_dir = os.path.dirname(__file__)
    unload_bay = os.path.join(parent_dir, "unload_bay")

    """Création de la baie si inexistante"""
    if os.path.isdir(unload_bay):
         print("Unload bay already exists")       
    else : 
        os.mkdir(unload_bay)

    original_rep = "original_room"
    originals = os.path.join(unload_bay, original_rep)
    if os.path.isdir(originals):
        print("Originals repository already exists")
    else :
        os.mkdir(originals)
        print("Originals repository created")
    
    copies_rep = "sorting_room"
    copies = os.path.join(unload_bay, copies_rep)
    if os.path.isdir(copies):
        print("Copies repository already exists")
    else :
        os.mkdir(copies)
        print("Copies repository created")

    report_rep = "reports"
    reports = os.path.join(unload_bay, report_rep)
    if os.path.isdir(reports):
        print("Reports repository already exists")
    else :
        os.mkdir(reports)
        print("Reports repository created")

    project_or = os.path.join(originals, project_n)
    if os.path.isdir(project_or):
        print("Project original repository already exists")
    else :
        os.mkdir(project_or)
        print("Project original repository created")

    project_cop = os.path.join(copies, project_n)
    if os.path.isdir(project_cop):
        print("Project copies repository already exists")
    else :
        os.mkdir(project_cop)
        print("Project copies repository created")
    
    """Création d'un dossier reports avec un sous-dossier 'reports'"""
    reports_project = os.path.join(reports, project_n)
    if os.path.isdir(reports_project):
        print("Reports sub repository already exists")
    else :
        os.mkdir(reports_project)
        print("Reports sub repository created")
    
    return project_or, project_cop, unload_bay, reports_project

def sail_to_bay(rep, originals, copies, unload_bay, report_r, user):
    
    """Calcul des hash dans le fichier racine"""
    for root, dirs, files in os.walk(rep): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)            
            file = Object(contentLocationValue=f, messageDigestAlgorithm="md5", messageDigest=md5)
            mets.set_object(file)
    for obj in mets.objects:
        print ("hash original", obj.messageDigest)



    event = Event("local", 1, eventType="message digest calculation", eventDateTime=horodatage())
    event.set_agent(user.agentName)
    mets.write_report("report.csv", report_r, type="hash")
    robot_copy(rep, originals, report_r)
    robot_copy(rep, copies, report_r)

    originals_hash_dict ={}
    """Calcul des hash dans originals et match avec registre"""
    for root, dirs, files in os.walk(originals): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)            
            file = Object(contentLocationValue=f, messageDigestAlgorithm="md5", messageDigest=md5)

    copies_hash_dict = {}
    """Calcul des hash dans copies et match avec registre"""
    for root, dirs, files in os.walk(copies): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)
            copies_hash_dict = {f, md5}            
            file = Object(contentLocationValue=f, messageDigestAlgorithm="md5", messageDigest=md5)



"""Etat des lieux"""
def state_of_art(rep, reports, us):
    start_depth = 1
    full_size = str(os.path.getsize(str(rep))) #taille du contenu de la totalité du répertoire en bytes
    date = horodatage() #horodatage du rapport
    stats = os.stat(rep)
    for root, dirs, files in os.walk(rep):
        current_depth = root.replace(rep, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = str(max(start_depth, current_depth)) #calcule la différence entre le niveau 1 et le compte des profondeurs

    state_report = State(rep, us.agentName, us.note, full_size, date, max_depth, stats)
    mets.write_report("audit_report.txt", reports, "state", cible= state_report)

"""Décompression des fichiers"""
def dezip(copies_rep):
    for root, dirs, files in os.walk(copies_rep):
        for file in files :
            f = os.path.join(root, file)
            if zipfile.is_zipfile(f):
                with zipfile.ZipFile(f, "r") as zip:
                    zip.extractall(root)
                    print("dezip done")

def droid_check():
    print("time to droid check")
    ...
"""Suppression de dossiers vides"""
def remove_empty(copies_rep):
    for root, dirs, files in os.walk(copies_rep):
        bytes = sum(os.path.getsize(os.path.join(root, file)) for file in files)
        if bytes == 0:
            print(root) #ajouter un tableau ou un rapport reprenant tous les dossiers vides et demande de confirmation avant de supprimer
            os.rmdir(root)
    print("Empty repertory removed")

def robot_copy(source, destination, log_repository):
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/e", "/copyall", f"/log+:{log_repository}/transfert_report.txt"], 
                    check=False)
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