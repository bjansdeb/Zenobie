import csv
import datetime 
import hashlib
import os
import re 
import subprocess
import sys
import zipfile
from errors import EmptyError
from models import Event, PremisObjects, State, File


"""-----------------------------------------------"""
"""            **** Functions   ****"""
"""-----------------------------------------------"""

"""Création et transfert vers la baie d'embarquement avec calcul hash"""

def create_bay(user, project_n, registre):
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

def create_objects(rep, report_r, user, registre):
    """Création des objets et calcul et détermination des hash dans le fichier racine"""

    for root, dirs, files in os.walk(rep): 
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)
            filename, file_extension = os.path.splitext(f)          
            obj = File(objectCategory="file", formatName=file_extension, contentLocationType="file path", contentLocationValue=f, messageDigestAlgorithm="md5", messageDigest=md5, originalName=filename)
            event = Event(eventType="digital signature generation", eventDateTime=horodatage(), eventDetail=obj.messageDigest, eventOutcome="success")
            event.add_linking_agent(user)
            obj.add_linking_event(event)
            event.add_linking_object(obj, "source")
            registre.add_event(event)              
            registre.add_object(obj)
            registre.add_uri(f, obj)
    #registre.get_uris()
    write_report("source_manifest_md5.csv", report_r, type="hash", cible=registre)

def sail_to_bay(rep, originals, copies, unload_bay, report_r, user, registre):
    
    # registre.write_report("hash_report.csv", report_r, type="hash")
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
    
    # for obj in registre.objects.values():
    #     if all(h in obj.messageDigest for h in originals_hash_dict):
    #         print("Integrity verification on originals is conform")
    #     else:
    #         print("Integrity verification on non originals is not conform")
    for obj in registre.objects.values():
        if obj.messageDigest in copies_hash_dict:
            old_location =  obj.contentLocationValue
            obj.contentLocationValue = copies_hash_dict[obj.messageDigest]
            event = Event(eventType="transfer", eventDateTime=horodatage(), eventOutcome="success", eventDetail=f"Transfer from {old_location} to {obj.contentLocationValue}")
            obj.add_linking_event(event)
            event.add_linking_object(obj, "outcome")
            registre.add_event(event)           
        else:
            old_location = obj.contentLocationValue
            event = Event(eventType="transfer", eventDateTime=horodatage(), eventOutcome="failure", eventDetail=f"Transfer from {old_location} to {obj.contentLocationValue} has failed")
            obj.add_linking_event(event)
            event.add_linking_object(obj, "outcome")
            registre.add_event(event)    
            print(f"warning, this object {obj} has a problematic check")
    write_report("moving_report.txt", report_r, "transfer", cible=registre )

"""Etat des lieux"""
def state_of_art(rep, reports, us, registre):
    start_depth = 1
    full_size = 0 
    files_number, repositories_number = 0, 0
    stats = os.stat(rep)
    state_report = State(rep, us.agentName, us.note, date=horodatage())
    tree = {}
    all_paths = [] #pour calculer le plus anciens/récents
    for root, dirs, files in os.walk(rep):
        current_depth = root.replace(rep, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = str(max(start_depth, current_depth)) #calcule la différence entre le niveau 1 et le compte des profondeurs
        repositories_number += 1
        
        tree[root] = {
            "dirs": dirs,
            "files": files
        }
        for file in files:
            fp = os.path.join(root, file)        
            full_size += os.path.getsize(fp)
            files_number += 1
            all_paths.append(fp)

    if all_paths:
        oldest_created_f = min(all_paths, key= os.path.getctime)
        oldest_ct = str(datetime.datetime.fromtimestamp(os.path.getctime(oldest_created_f)))
        most_recent_created_f = max(all_paths, key=os.path.getctime)
        most_rct = str(datetime.datetime.fromtimestamp(os.path.getctime(most_recent_created_f)))
        oldest_modified_f = min(all_paths, key= os.path.getmtime)
        oldest_mt = str(datetime.datetime.fromtimestamp(os.path.getctime(oldest_modified_f)))
        most_recent_modified_f = max(all_paths, key= os.path.getmtime)
        most_rmt = str(datetime.datetime.fromtimestamp(os.path.getctime(most_recent_modified_f)))

    state_report.full_size=full_size
    state_report.stats = stats
    state_report.repositories_number= repositories_number
    state_report.files_number=files_number
    state_report.oldest_created_file = oldest_created_f
    state_report.oldest_created_time = oldest_ct
    state_report.most_recent_created_file =most_recent_created_f
    state_report.most_recent_created_time= most_rct
    state_report.oldest_modified_file = oldest_modified_f
    state_report.oldest_modified_time = oldest_mt
    state_report.most_recent_modified_file = most_recent_modified_f
    state_report.most_recent_modified_time = most_rmt
    state_report.list_dir = tree
    state_report.depth = max_depth
    registre.add_event(Event(eventType="appraisal", eventDateTime=horodatage(), eventDetail= state_report, eventOutcome="success"))
    write_report("initial_audit_report.txt", reports, "state", cible= state_report)

"""Décompression des fichiers"""
def dezip(copies_rep, registre):
    for root, dirs, files in os.walk(copies_rep):
        for file in files :
            f = os.path.join(root, file)
            if zipfile.is_zipfile(f):
                with zipfile.ZipFile(f, "r") as zip:
                    zip.extractall(root)
                    print("dezip done")
                    registre.add_event(Event(eventType="unpacking", eventDetail="Unpacked from : {f}", eventDateTime=horodatage()))
                    #Exemple archivematica <premis:eventDetail>Unpacked from: %transferDirectory%objects/Project.zip (63706dd1-6f8f-4460-a5a5-546bac061d91)</premis:eventDetail>

def droid_check(rep, reports, registre):
    
    """à rajouter plus tard, pour obtenir certains types de métadonnées"""
    #$ droid -co NAME PUID -a file.jpg
    #"NAME","PUID"
    #"file.jpg","fmt/1507"
    """"""
    result = subprocess.run(["droid.bat", "-a", rep, "-R"], text=True, capture_output=True, check=True)
    write_report("droid_report.txt", reports, "droid", result)

"""Suppression de dossiers vides"""
def remove_empty(copies_rep, registre):
    for root, dirs, files in os.walk(copies_rep):
        bytes = sum(os.path.getsize(os.path.join(root, file)) for file in files)
        if bytes == 0:
            print(root) #ajouter un tableau ou un rapport reprenant tous les dossiers vides et demande de confirmation avant de supprimer
            os.rmdir(root)
    print("Empty repertory removed")

def remove_forbidden_chars(rep, report_r, registre):
    #à corriger pour n'obtenir que le nom de fichier sans l'extension, car bugue avec noms de fichier "nom_3.5.5.py"
    for root, dirs, files in os.walk(rep):
        for file in files:
            f = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file)  
            file_lowered = filename.lower()
            pattern = re.compile(r"[@\[\[\.<>:\"\'/\\|?*\x00-\x1F]")
            corrected_name = pattern.sub("-", file_lowered).replace(" ", "-")
            corrected_file_n = corrected_name + file_extension
            corrected_f = os.path.join(root, corrected_file_n)
            os.rename(f, corrected_f)
            registre.add_event(Event(eventType="filename change", eventDateTime=horodatage(), eventDetail=f"Original name: {filename} - New name: {corrected_file_n}"))
    write_report("rename_report.txt", report_r, type="rename", cible=registre)
    
def robot_copy(source, destination, log_repository):
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/e", "/copyall", f"/log+:{log_repository}/transfert_report.txt"], 
                    check=False)
    #robotcopy contient de nombreuses métadonnées qu'on pourrait utiliser pour le rapport ultérieurement

def hash_calculator(source):
    # sha_256 = hashlib.sha256() #à décocher si on veut cet algo à la place de md5
    md5 = hashlib.md5()
    #print(source)
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

def write_report(file_name, path, type, cible= None):
    """
    Docstring for write_report
    Function d'écriture des rapports
    :param file_name: Nom du fichier
    :param path: Emplacement
    :param type: hash, state, event, transfer, rename
    :param cible: objet sur lequel porte le rapport
    """
    file = os.path.join(path, file_name)
    match type:
        case "droid":
            with open(file, "w+t", encoding="utf-8") as droid_r:
                droid_r.write("Droid identification report")
                droid_r.write(f"{cible.stdout}")
        case "hash":
            with open(file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_name', 'hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for object in cible.objects.values() :
                    writer.writerow({'object_name': {object.contentLocationValue}, 'hash': {object.messageDigest}})
            print(f"Hash report done, see {file}")

        case "state":           
            with open(file, "w+t", encoding="utf-8") as state_r:
                state_r.write(f"Audit of {cible.title}")
                state_r.write(f"\nSize of the repository :{cible.full_size} bytes")
                state_r.write(f"\nMax-depth: {cible.depth}")
                state_r.write(f"\nStats : {cible.stats}")
                state_r.write(f"\nNumber of files : {cible.files_number}")
                state_r.write(f"\nNumber of repositories : {cible.repositories_number}")
                state_r.write("\n*Please, note that the indicated dates depend on the operating system and may considerably changed from a system to another*")
                state_r.write(f"\nOldest created file : {cible.oldest_created_file} at {cible.oldest_created_time}")
                state_r.write(f"\nMost recent created file : {cible.most_recent_created_file} at {cible.most_recent_created_time}")
                state_r.write(f"\nOldest modified file : {cible.oldest_modified_file} at {cible.oldest_modified_time}")
                state_r.write(f"\nMost recent modified file : {cible.most_recent_modified_file} at {cible.most_recent_modified_time}")                
                state_r.write(f"\nReport done with Zenobie at {cible.date} by {cible.author} ({cible.role})")
                state_r.write(f"\nContent:")
                for path, content in cible.list_dir.items():
                    state_r.write(f"\n {path}\n")

                    for d in content["dirs"]:
                        state_r.write(f"   |── {d}/\n")

                    for f in content["files"]:
                        state_r.write(f"   |── {f}\n")
            print(f"Audit done, see {file}")
 
        case "event":
            with open(file, "w+t", encoding="utf-8") as event_r:
                event_r.write(f"\nEvents report")
                for event in cible.events.values():
                    event_r.write("\n----------------\n")
                    event_r.write(f"\nEvent: {event.eventType}")
                    event_r.write(f"\nEvent id type: {event.eventIdentifierType}")
                    event_r.write(f"\nEvent id: {event.eventIdentifierValue}")
                    event_r.write(f"\nEvent date time: {event.eventDateTime}")
                    event_r.write(f"\nEvent detail: {event.eventDetail}")
                    for items in event.linkingObjectIdentifier :
                        event_r.write(f"\nCible object identifier: [{items.linkingObjectIdentifierType}] {items.linkingObjectIdentifierValue} ")
            print(f"Events report done, see {file}")
        
        case "transfer":
            with open(file, "w+t", encoding="utf-8") as transf_r:
                transf_r.write(f"Transfert report")
                for event in cible.events.values():
                    if event.eventType == "transfer":
                        transf_r.write(f"\nEvent id type: {event.eventIdentifierType}")
                        transf_r.write(f"\nEvent id: {event.eventIdentifierValue}")
                        transf_r.write(f"\nEvent date time: {event.eventDateTime}")
                        transf_r.write(f"\nEvent detail: {event.eventDetail}")
                        for items in event.linkingObjectIdentifier:
                            transf_r.write(f"\nCible object identifier: [{items.linkingObjectIdentifierType}] {items.linkingObjectIdentifierValue}")
            print(f"Transfer report done, see {file}")

        case "rename":
            with open(file, "w+t", encoding="utf-8") as rename_r:
                for event in cible.events.values():
                    if event.eventType == "filename change":
                        rename_r.write(f"\nEvent id type: {event.eventIdentifierType}")
                        rename_r.write(f"\nEvent detail: {event.eventDetail}")
                        for items in event.linkingObjectIdentifier:
                            transf_r.write(f"\nCible object identifier: [{items.linkingObjectIdentifierType}] {items.linkingObjectIdentifierValue}")

            print(f"Rename report done, see {file}")
