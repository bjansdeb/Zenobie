import csv
import datetime 
import hashlib
import json
import os
import py7zr
import re 
import subprocess
import stat
import sys
import tarfile
import zipfile

from config import read_config
from errors import EmptyError
from log import log_it
from pathlib import Path
from reporting import write_report
from models import Event, PremisObjects, State, File


config_data = read_config()
MAX_FILES = int(config_data['max_files'])
MAX_TOTAL_SIZE = int(config_data['max_total_size'])
AUTHORIZED_PACKS = config_data['authorized_packs']
UNAUTHORIZED_PACKS = config_data['unauthorized_packs']
FORBIDDEN_CHARS = re.compile(r"[\@\]\[\^\<\>\:\"\'\{\}\/\|\?\*\x00-\x1F]")


"""-----------------------------------------------"""
"""            **** Functions principales  ****   """
"""-----------------------------------------------"""

"""Création et transfert vers la baie d'embarquement avec calcul hash"""

def create_bay(user, project_n: str, registre) -> dict:
    log_it("info","Creating bay...")
    parent_dir = os.path.dirname(__file__)
    filename, _ = os.path.splitext(project_n)  
    project = os.path.join(parent_dir, filename + "_project") #ajoute un dossier de projet avec le nom du fonds d'origine
    unload_bay = os.path.join(project, "unload_bay")

    """Création du dossier projet si inexistant"""
    if os.path.isdir(project):
         log_it("warning","Unload bay already exists")
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

    """
    Création de la baie si inexistant
    """
    if os.path.isdir(unload_bay):
         log_it("warning","Unload bay already exists")       
    else : 
        os.mkdir(unload_bay)
        log_it("info", "Unload bay repository created")

    """
    Création du répertoire avec originaux si inexistant
    """
    original_rep = "original_room"
    originals = os.path.join(unload_bay, original_rep)
    if os.path.isdir(originals):
        log_it("warning","Originals repository already exists")
    else :
        os.mkdir(originals)
        log_it("info", "Originals repository created")
    
    """
    Création du répertoire de travail si inexistant
    """
    copies_rep = "sorting_room"
    copies = os.path.join(unload_bay, copies_rep)
    if os.path.isdir(copies):
        log_it("warning","Copies repository already exists")
    else :
        os.mkdir(copies)
        log_it("info","Copies repository created")

    """
    Création du dossier de rapports si inexistant
    """
    report_rep = "reports"
    reports = os.path.join(unload_bay, report_rep)
    if os.path.isdir(reports):
        log_it("warning","Reports repository already exists")
    else :
        os.mkdir(reports)
        log_it("info","Reports repository created")

    """
    Création du sous-dossier de projet contenant les originaux si inexistant
    """
    project_or = os.path.join(originals, project_n)
    if os.path.isdir(project_or):
        log_it("warning","Project original repository already exists")
    else :
        os.mkdir(project_or)
        log_it("info","Project original repository created")


    """
    Création du sous-dossier de projet contenant les copies de travail si inexistant
    """
    project_cop = os.path.join(copies, project_n)
    if os.path.isdir(project_cop):
        log_it("warning","Project copies repository already exists")
    else :
        os.mkdir(project_cop)
        log_it("info","Project copies repository created")
    
    """
    Création d'un sous-dossier de reporting dans report avec nom du projet
    '"""
    reports_project = os.path.join(reports, project_n)
    if os.path.isdir(reports_project):
        log_it("warning","Reports sub repository already exists")
    else :
        os.mkdir(reports_project)
        log_it("info","Reports sub repository created")

    paths = {'originals' : project_or, 'copies': project_cop, 'unload_bay': unload_bay, 'reports': reports_project}
    
    return paths

def create_objects(rep, report_r, user, registre):
    """
    Création des objets et calcul et détermination des hash dans le fichier racine
    """

    for root, _, files in os.walk(rep):  #_ était dirs
        for file in files :
            f =os.path.join(root, file)
            md5 = hash_calculator(f)
            relative_path =  get_relative_path(f, rep) #f seul auparavant
            filename, file_extension = os.path.splitext(f)          
            
            obj = File(objectCategory="file", formatName=file_extension, contentLocationType="file path", 
                       contentLocationValue=relative_path, messageDigestAlgorithm="md5", 
                       messageDigest=md5, originalName=filename)
            
            event = Event(eventType="digital signature generation", eventDateTime=horodatage(), 
                          eventDetail=obj.messageDigest, eventOutcome="success")
            
            event.add_linking_agent(user)
            obj.add_linking_event(event)
            event.add_linking_object(obj, "source")
            
            registre.add_event(event)              
            registre.add_object(obj)
            registre.add_uri(f, obj)
    #registre.get_uris()

    write_report("source_manifest_md5.csv", report_r, type="hash", cible=registre)

def sail_to_bay(rep, originals, copies, unload_bay, report_r, user, registre):
    """
    fonction de transfert vers les répertoires de traitement et de sauvegarde
    :param rep: Répertoire source
    :param originals: Répertoire de sauvegarde des originaux
    :param copies: Répertoire de traitement 
    """


    """première itération avec les originaux"""
    paths_destination = robo_copy(rep, originals, report_r, "robocopy_transfer_originals_report.txt", registre)
    integrity_problems = verify_hashs_and_paths(paths_destination, registre)
    paths_destination.clear()

    if integrity_problems :
        write_report(integrity_problems, "hash_problems_with_originals.txt", report_r) # à améliorer
        integrity_problems.clear()

    """deuxième itération avec les copies"""
    paths_destination = robo_copy(rep, copies, report_r, "robocopy_transfer_copies_report.txt", registre)
    integrity_problems = verify_hashs_and_paths(paths_destination, registre)
    paths_destination.clear()

    if integrity_problems :
        write_report(integrity_problems, "hash_problems_with_copies.txt", report_r)
        integrity_problems.clear()

    
    """
    Match des hash de registre objects avec copies_hash_dict pour metre à jour l'emplacement des objets
    """
    for obj in registre.objects.values():
        if obj.messageDigest in copies_hash_dict:
            old_location =  obj.contentLocationValue
            obj.contentLocationValue = copies_hash_dict[obj.messageDigest]
            event = Event(eventType="transfer", eventDateTime=horodatage(), eventOutcome="success", 
                          eventDetail=f"Transfer from {old_location} to {obj.contentLocationValue}")
            obj.add_linking_event(event)
            event.add_linking_object(obj, "outcome")
            registre.add_event(event)           

        else:
            old_location = obj.contentLocationValue
            event = Event(eventType="transfer", eventDateTime=horodatage(), eventOutcome="failure", 
                          eventDetail=f"Transfer from {old_location} to {obj.contentLocationValue} has failed")
            obj.add_linking_event(event)
            event.add_linking_object(obj, "outcome")
            registre.add_event(event)    
            log_it("warning",f"warning, this object {obj} has a problematic check")

    write_report("moving_report.txt", report_r, "transfer", cible=registre )


"""Etat des lieux"""
def state_of_art(rep, reports, us, registre):
    log_it("info","Start of the files audit")
    start_depth = 1
    repositories_number = 0
    files_number = 0
    full_size = os.path.getsize(str(rep)) #taille du contenu de la totalité du répertoire en bytes
    date = horodatage() #horodatage du rapport
    state_report = State(rep, us.agentName, us.note, date=horodatage())
    tree = {}
    all_paths = [] #pour calculer le plus anciens/récents
    for root, dirs, files in os.walk(rep):
        current_depth = root.replace(rep, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = str(max(start_depth, current_depth)) #calcule la différence entre le niveau 1 et le compte des profondeurs
        print(root, type(root))
        if os.path.isdir(root):
            repositories_number += 1
        
        tree[root] = {
            "dirs": dirs,
            "files": files
        }
        for file in files:
            fp = os.path.join(root, file)        
            full_size += os.path.getsize(fp)
            if os.path.isfile(file):
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

    state_report.date = date
    state_report.full_size=full_size
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
    log_it("info", "Audit succesfully finished")

"""Décompression des fichiers"""
def dezip(copies_rep, registre):
    """
    Docstring for dezp
    Fonction de décompression
    :param copies_rep: path : attention, ne prend que des répertoires, pas des fichiers
    """

    exceeding_packs = []
    uncompliant_packs = []
    archives_to_unpack = []
    for root, _, files in os.walk(copies_rep):
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

    registre.add_event(Event(eventType="unpacking", eventDetail="Unpacked from : {f}", eventDateTime=horodatage()))
    #Exemple archivematica <premis:eventDetail>Unpacked from: %transferDirectory%objects/Project.zip (63706dd1-6f8f-4460-a5a5-546bac061d91)</premis:eventDetail>
   
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

        if os.path.isdir(file_n):
            new_path = verify_collision(file_n)
        os.mkdir(new_path)
        log_it("info",f"New reposit created during dezip process {new_path}")       
        z.extractall(new_path)

        log_it("info",f"{old_path} extracted")
    remove_pack(old_path)

"""Analyse des formats avec DROID"""
def droid_check(rep, reports, registre): 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    droid_path = os.path.join(base_dir, "droid", "droid.bat") #subprocess refuse les chemins relatifs

    if os.path.isfile(droid_path):
        try:
            log_it("info", "DROID has been launched, please note that that can take a few minutes...")
            result = subprocess.run([droid_path, "-a", rep,"-Pr", "profile.generateHash=true", "-R"], text=True, capture_output=True, check=True)
            write_report("droid_report.csv", reports, "droid", result)
            log_it("info", "DROID has successfully finished ! " \
            f"You can see the report into {reports}")      
            registre.add_event(Event(eventType="validation", eventDateTime=horodatage(), eventOutcome="success"))
        except subprocess.CalledProcessError as e:
            print(e.stderr, e.stdout)

    else :
        log_it("error","droid check has failed because droid.bat is not present on the Zenobie repository (droid/droid.bat). " \
        "Please install it and retry")


def get_droid_data():
    if os.path.isfile("droid_report.csv"):
        with open("droid_report.csv", "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                print(row.get("NAME"))
                row.get("FILE_PATH")
                row.get("PUID")
                print(row.get("MIME_TYPE"))
                print(row.get("HASH"))
    else:
        log_it("error", "Zenobie does not find the droid_report.csv file")   

def remove_empty(copies_rep, report_r, registre):
    #peut-être penser à inclure un dry run
    log_it("info","Removing empty repositories has started")
    abs_path = os.path.abspath(copies_rep) #abspath retourne le chemin absolu exact de l'objet, utile pour vérifier des paths relatifs
    if not os.path.isdir(abs_path):
        raise ValueError(f"Directory does not exist: {abs_path}")
    elif is_dangerous_root(abs_path): 
        raise ValueError(f"Dangerous path refused: {abs_path}")
    log_it("info",f"Zenobie has checked {abs_path} before the removing process. The path is secure")

    removed = 0 
    initial_root = abs_path
    for root, dirs, files in os.walk(abs_path, topdown=False):
        try:
            if root == initial_root:
                continue
            if not os.listdir(root):
                os.rmdir(root) 
                log_it("info",f"Removed: {root}")
                registre.add_event(Event(eventType="deletion", eventDateTime=horodatage(), eventDetail=f"{root} was empty and has been removed"))
                removed += 1
        except Exception as e:
            log_it("error",f"Error on {root}: {e}")         
    log_it("info",f"Removing process done. Zenovie has removed {removed} empty repositories")

def remove_forbidden_chars(rep, report_r, registre):
    log_it("info", "launch of forbidden chars removing")
    #peut-être penser à mettre un dry run
    for root, dirs, files in os.walk(rep):
        for file in files:
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file) 
            if not filename:
                filename = "unnamed"

            if re.search(FORBIDDEN_CHARS, filename):
                filename = FORBIDDEN_CHARS.sub("-", filename)
            
            filename = filename.replace(" .", ".")
            filename = filename.replace(" ", "_")
            new_filename = filename + file_extension
            new_path = os.path.join(root, new_filename)
            if new_path == old_path:
                continue

            normalized_name = verify_collision(new_path)      
            try:
                os.rename(old_path, normalized_name)
                registre.add_event(Event(eventType="filename change", eventDateTime=horodatage(), eventDetail=f"Original name: {filename} - New name: {normalized_name}"))

            except FileExistsError:
                raise FileExistsError("There is a collision between two files names")
            except PermissionError:
                raise PermissionError("You don't have the permission to modify the file, please run Zenobie again with ")
            except OSError as e:
                raise OSError(f"Zenobie failed to rename {old_path}: {e}")
            
    write_report("rename_report.txt", report_r, type="rename", cible=registre)
    log_it("info", "removing of forbidden chars done")


"""-----------------------------------------------"""
"""            **** Functions secondaires  ****   """
"""-----------------------------------------------"""

def robo_copy(source: str, destination: str, log_repository: str, report_name: str, registre: PremisObjects) -> dict:

    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    process = subprocess.run(["robocopy", source, destination,
                    "/e", "/copy:DATSO", f"/log+:{log_repository}/{report_name}", "/X", "/V", "/FP", "/TEE"], 
                    check=False) #/copyall changé en /copy:DATSO
    if process.returncode == 1 :
        log_it("info", "robot_copy successful finished")
        event = Event(eventType="transfer", eventDateTime=horodatage(), 
        eventDetail= f"Robocopy process finished", eventOutcome="success")
        registre.add_event(event)        
        
    else:
        log_it("error", f"robot_copy has encounter an error \nplease check the {log_repository}/{report_name} to fix it before retry the process")
        while True:
            try:
                answeer = str(input("Do you want to continue despite this problem (yes/no)?")).lstrip().lower()
                if answeer == "yes":
                    log_it("info","Ok, we continue without removing the empty repositories")
                    break
                elif answeer == "no":
                    log_it("info","Ok, exiting the script because of robocopy problem")
                    sys.exit()
            except EmptyError:
                log_it("warning","Please, answeer by yes or no ")

    paths_destination = get_relative_paths(destination)
    return paths_destination
    

def hash_calculator(source):
    # sha_256 = hashlib.sha256() #à décocher si on veut cet algo à la place de md5
    md5 = hashlib.md5()
    #print(source)
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

# hash_match(registre, originals_hash_dict, "hash_problems_with_originals.txt", report_r)

def hash_match(source: object, cible: dict, report_name: str, report_r):
    files_with_hash_problem = {}
    for obj in source.objects.values():
        if obj.messageDigest in cible:
            event = Event(eventType="digital signature validation", eventDateTime=horodatage(), 
            eventDetail= f"{cible[obj.messageDigest]} is conform. {obj.messageDigest} matches", eventOutcome="success")
            source.add_event(event)
        else :
            event = Event(eventType="digital signature validation", eventDateTime=horodatage(), 
            eventDetail= f"{cible[obj.messageDigest]} is not conform. {obj.messageDigest} does not match", eventOutcome="failure")
            source.add_event(event)
            files_with_hash_problem[obj.messageDigest] = cible[obj.messageDigest]
            
    if files_with_hash_problem :
        write_report(report_name, report_r, "unmatched_hash", files_with_hash_problem)
        log_it("warning", f"There are original files inside the originals repository that encounter integrity problems. You can check these here : {report_r}/hash_problems_with_originals.txt")
        files_with_hash_problem.clear()

def verify_hashs_and_paths(paths_destination: dict, registre: PremisObjects) ->dict:
    """ Vérifie les hashs et les chemins récoltés dans paths_destination avec les chemins et hash contenus dans les objets de métadonnées"""
    integrity_problems ={}
    for obj in registre.objects.values():
        if obj.messageDigest in paths_destination:
            if obj.contentLocationValue == paths_destination[obj.messageDigest]:
                event = Event(eventType="digital signature validation", eventDateTime=horodatage(), 
                eventDetail= f"{paths_destination[obj.messageDigest]} is conform. {obj.messageDigest} matches", eventOutcome="success")
                registre.add_event(event)
                continue
            else:
                event = Event(eventType="digital signature validation", eventDateTime=horodatage(), 
                eventDetail= f"{paths_destination[obj.messageDigest]} is not conform. {obj.messageDigest} does not match", eventOutcome="failure")
                registre.add_event(event)
                integrity_problems[paths_destination[obj.messageDigest]] = f"Hash {paths_destination[obj.messageDigest]} does not match any path in the source repository"
        else:
            integrity_problems[paths_destination[obj.messageDigest]] = f"{obj.messageDigest} has not equivalent path in the source repository"
    if integrity_problems:
        log_it("warning", "There are integrity problems with some displaced files")
        return integrity_problems

    else:
        log_it("info", "integrity check done without problems")        


def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

def is_dangerous_root(path):
    path = os.path.abspath(path)

    # si le chemin absolu indiqué correspond à la racine du système
    if os.path.abspath(path) == os.path.abspath(os.sep):
        return True

    # vérifie si le chemin donné n'est pas D:/, C:/, etc...
    if os.name == "nt":
        drive, tail = os.path.splitdrive(path)
        if path == drive + os.sep:
            return True

    home = os.path.abspath(os.path.expanduser("~"))
    try:
        if os.path.samefile(path, home):
            return True
    except FileNotFoundError:
        pass

    return False

def verify_collision(n_path):
    base, ext = os.path.splitext(n_path)
    counter = 0
    candidate = n_path
    while os.path.exists(candidate):
            counter +=1
            candidate = f"{base}_{counter}{ext}"
    return candidate

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

def get_relative_path(child_path: str, absolute_parent_path: str) -> str:
    """Calcule le chemin relatif pour un chemin individuel donné à partir du répertoire parent absolu"""
    child = Path(child_path)
    parent = Path(fr'{absolute_parent_path}')
    path = parent.name / child.relative_to(parent)
    return path

def get_relative_paths(source : str) -> dict:
    """Calcule le chemin relatif pour un répertoire entier et les place dans un array avec leur hash comme key"""
    paths_array = { }
    path = os.walk(source)
    for root, _, files in path :
        for file in files:
            filename = os.path.join(root, file)
            p = Path(filename)
            source_p = Path(fr'{source}')
            hash_output = hash_calculator(filename)
            paths_array[hash_output] = source_p.name / p.relative_to(source_p)
    return paths_array

def serialize(object):
    return json.dumps(object)

def deserialize(json_file):
    return json.loads(json_file)