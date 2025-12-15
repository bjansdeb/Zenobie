import datetime 
import hashlib
import os
import re 
import subprocess
import sys
import zipfile
from errors import EmptyError
from models import Event, Object, State


"""-----------------------------------------------"""
"""            **** Functions   ****"""
"""-----------------------------------------------"""

"""Création et transfert vers la baie d'embarquement avec calcul hash"""

def create_bay(user, project_n, mets):
    parent_dir = os.path.dirname(__file__)
    filename, file_extension = os.path.splitext(project_n)  
    project = os.path.join(parent_dir, filename + "_project") #ajoute un dossier de projet avec le nom du fonds d'origine
    unload_bay = os.path.join(project, "unload_bay")

    """Création du projet si inexistant"""
    if os.path.isdir(project):
         print("Unload bay already exists")
         while True :
            try:
                answeer = input("Warning, this project already exists. Do you want continue(yes/no) ? If 'no' you will exit the program:").lstrip().lower()       
                if answeer == "yes":
                    break
                elif answeer == "no":
                    sys.exit()
                else : 
                    raise EmptyError    
            except EmptyError:
                print("please, answeer by yes or no") 

    else : 
        os.mkdir(project)

    """Création de la baie si inexistant"""
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

def create_objects(rep, report_r, user, mets):
    """Création des objets et calcul et détermination des hash dans le fichier racine"""
    for root, dirs, files in os.walk(rep): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)  
            filename, file_extension = os.path.splitext(f)          
            file = Object(formatName=file_extension, contentLocationValue=f, messageDigestAlgorithm="md5", messageDigest=md5, originalName=filename)
            event = Event(eventType="digital signature generation", eventDateTime=horodatage())
            event.set_agent(user.agentIdentifierType, user.agentIdentifierValue, user.agentType)
            mets.set_event(event)
            mets.set_object(file)


    mets.write_report("source_manifest_md5.csv", report_r, type="hash")

def sail_to_bay(rep, originals, copies, unload_bay, report_r, user, mets):
    
    # mets.write_report("hash_report.csv", report_r, type="hash")
    robot_copy(rep, originals, report_r)
    robot_copy(rep, copies, report_r)
    #Event("replication")
    #Event("transfert")

    originals_hash_dict ={}
    """Calcul des hash dans originals et match avec registre"""
    for root, dirs, files in os.walk(originals): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f) 
            originals_hash_dict [md5] = f           

    copies_hash_dict = {}
    """Calcul des hash dans copies et match avec registre"""
    for root, dirs, files in os.walk(copies): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)
            copies_hash_dict [md5] = f            

    
    for obj in mets.objects:
        if all(h in obj.messageDigest for h in originals_hash_dict):
            ...
            # print(obj, "Integrity verification is conform")
        else:
            ...
            # print(obj, "this item has an integrity problem")

    for obj in mets.objects:
        if all(h in obj.messageDigest for h in copies_hash_dict):
            ...
            # print(obj, "Integrity verification is conform")
        else:
            ...
            # print(obj, "this item has an integrity problem")

    mets.set_event(Event(eventType="digital signature validation", eventDateTime=horodatage()))

"""Etat des lieux"""
def state_of_art(rep, reports, us, mets):
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
def dezip(copies_rep, mets):
    for root, dirs, files in os.walk(copies_rep):
        for file in files :
            f = os.path.join(root, file)
            if zipfile.is_zipfile(f):
                with zipfile.ZipFile(f, "r") as zip:
                    zip.extractall(root)
                    print("dezip done")
                    mets.set_event(Event(eventType="Decompression", eventDateTime=horodatage()))
                


def droid_check(repository, mets):
    print("time to droid check")
    ...
"""Suppression de dossiers vides"""
def remove_empty(copies_rep, mets):
    for root, dirs, files in os.walk(copies_rep):
        bytes = sum(os.path.getsize(os.path.join(root, file)) for file in files)
        if bytes == 0:
            print(root) #ajouter un tableau ou un rapport reprenant tous les dossiers vides et demande de confirmation avant de supprimer
            os.rmdir(root)
    print("Empty repertory removed")

def remove_forbidden_chars(repository, mets):
    for root, dirs, files in os.walk(repository):
        for file in files:
            file_lowered = file.lower()
            matches = re.search(r"^(.+).(.+)$", file_lowered)
            uncorrect_name = matches.group(1)
            pattern = re.compile(r"@[\.<>:\"\'/\\|?*\x00-\x1F]")
            corrected_name = pattern.sub("", uncorrect_name).replace(" ", "-")
            corrected_file_n = corrected_name + matches.group(2)
            os.rename(file, corrected_file_n)


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