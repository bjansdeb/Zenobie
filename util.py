import csv
import datetime 
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
from helpers import *
from reporting import write_report, read_json_report, write_json_report
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

def size_name_check(repository_path : str) -> int:
    """
    Retourne la taille du nom de chemin le plus long dans l'arborescence
    """
    higher_size = 0
    for root, _, files in os.walk(repository_path):  #_ était dirs
        for file in files :
            file_path_name =os.path.join(root, file)
            size_path = len(file_path_name)
            if size_path > higher_size:
                higher_size = size_path
    return higher_size

def create_bay(project_name: str) -> dict:
    """
    Retourne les chemins créés pour le projet
    """
    log_it("info","Creating bay...")
    parent_dir = os.path.dirname(__file__)
    filename, _ = os.path.splitext(project_name)  
    project = os.path.join(parent_dir, filename + "_arch") #ajoute un dossier de projet avec le nom du fonds d'origine
    unload_bay = os.path.join(project, "unload_bay")

    """Création du dossier projet si inexistant"""
    if os.path.isdir(project):
         log_it("warning","Unload bay already exists")
         while True :
            try:
                answeer = input("Warning, this project already exists. Do you want continue(yes/no) ? " \
                "If 'no' you will exit the program:").lstrip().lower()       
                if answeer == "yes":
                    break
                elif answeer == "no":
                    sys.exit()
                else : 
                    raise EmptyError    
            except EmptyError:
                log_it("info", "please, answeer by yes or no") 

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
    original_rep = "orig_room"
    originals = os.path.join(unload_bay, original_rep)
    if os.path.isdir(originals):
        log_it("warning","Originals repository already exists")
    else :
        os.mkdir(originals)
        log_it("info", "Originals repository created")
    
    """
    Création du répertoire de travail si inexistant
    """
    copies_rep = "sort_room"
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
    project_or = os.path.join(originals, project_name)
    if os.path.isdir(project_or):
        log_it("warning","Project original repository already exists")
    else :
        os.mkdir(project_or)
        log_it("info","Project original repository created")

    """
    Création du sous-dossier de projet contenant les copies de travail si inexistant
    """
    project_cop = os.path.join(copies, project_name)
    if os.path.isdir(project_cop):
        log_it("warning","Project copies repository already exists")
    else :
        os.mkdir(project_cop)
        log_it("info","Project copies repository created")

    paths = {'originals' : project_or, 'copies': project_cop, 'unload_bay': unload_bay, 'reports': reports}
    
    return paths

def create_objects(source_path, report_repository, user, registre):
    """
    Création des objets et calcul et détermination des hash dans le fichier racine
    """

    for root, _, files in os.walk(source_path):  #_ était dirs
        for file in files :
            f =os.path.join(root, file)
            if os.path.isfile(f):
                sha_256 = hash_calculator(f)
                relative_path = get_relative_path(f, source_path) #f seul auparavant
                filename, file_extension = os.path.splitext(f)          
                
                premis_object = File(objectCategory="file", 
                           formatName=file_extension, 
                           contentLocationType="file path", 
                           contentLocationValue=relative_path, 
                           messageDigestAlgorithm="sha 256", 
                           messageDigest=sha_256, 
                           originalName=filename)
                
                event = Event(eventType="digital signature generation", 
                              eventDateTime=horodatage(), 
                              eventDetail=premis_object.messageDigest, 
                              eventOutcome="success")
                
                event.add_linking_agent(user)
                premis_object.add_linking_event(event)
                event.add_linking_object(premis_object, "source")
                
                registre.add_event(event)              
                registre.add_object(premis_object)
                registre.add_absolute_path(f, premis_object.objectIdentifierValue)

    write_report("source_manifest_sha256.csv", report_repository, type="hash", cible=registre)
    log_it("info", "writing source_manifest_sha256.csv")

    
def sail_to_bay(source_path, originals, copies, report_repository, user, registre):
    """
    fonction de transfert vers les répertoires de traitement et de sauvegarde
    :param rep: Répertoire source
    :param originals: Répertoire de sauvegarde des originaux
    :param copies: Répertoire de traitement 
    """

    """première itération avec les originaux"""
    paths_destination = robo_copy(source_path, originals, report_repository, "robocopy_transfer_originals_report.txt", user, registre)
    integrity_problems = verify_hashs_and_paths(paths_destination, registre)
    paths_destination.clear()

    if integrity_problems :
        log_it("warning", "there were integrity problems during the migration to the originals repository. " \
        "Take a look at the reports")
        write_report("hash_problems_with_originals.txt", report_repository, "integrity", dict_cible=integrity_problems) 
        integrity_problems.clear()
    else:
        log_it("info", "hash and path verification done without problems for originals repository")


    """deuxième itération avec les copies"""
    paths_destination = robo_copy(source_path, copies, report_repository, "robocopy_transfer_copies_report.txt", user, registre)
    

    integrity_problems = verify_hashs_and_paths(paths_destination, registre)
    paths_destination.clear()

    if integrity_problems :
        log_it("warning", "there were integrity problems during the migration to the sorting repository. " \
        "Take a look at the reports")
        write_report("hash_problems_with_copies.txt", report_repository, "integrity", dict_cible=integrity_problems)
        integrity_problems.clear()
    else:
        log_it("info", "hash and path verification done without problems for sorting repository")

    write_report("moving_report.txt", report_repository, "transfer", cible=registre )
    log_it("info", "writing moving_report.txt")



"""Etat des lieux"""
def state_of_art(source_path, report_repository, user, registre):
    log_it("info","Start of the files audit")
    start_depth = 1
    repositories_number = 0
    files_number = 0
    full_size = os.path.getsize(str(source_path)) #taille du contenu de la totalité du répertoire en bytes
    date = horodatage() #horodatage du rapport
    state_report = State(source_path, user.agentName, user.note, date=horodatage())
    tree = {}
    all_paths = [] #pour calculer le plus anciens/récents
    all_extensions = []
    for root, dirs, files in os.walk(source_path):
        current_depth = root.replace(source_path, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = str(max(start_depth, current_depth)) #calcule la différence entre le niveau 1 et le compte des profondeurs
        if os.path.isdir(root):
            repositories_number += 1
        
        tree[root] = {
            "dirs": dirs,
            "files": files
        }
        for file in files:
            file_path = os.path.join(root, file)        
            full_size += os.path.getsize(file_path)
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() not in all_extensions:
                all_extensions.append(file_extension.lower())

            if os.path.isfile(file):
                files_number += 1
            all_paths.append(file_path)

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
    state_report.extensions = all_extensions

    event = Event(eventType="appraisal", eventDateTime=horodatage(), eventDetail= state_report, eventOutcome="success")
    event.add_linking_agent(user)
    registre.add_event(event)

    write_report("initial_audit_report.txt", report_repository, "state", cible= state_report)
    log_it("info", "Writing initial_audit_report.txt")
    log_it("info", "Audit succesfully finished")

"""Décompression des fichiers"""
def dezip(copies_rep, report_path, user, registre):
    """
    Fonction de décompression
    :param copies_rep: path attention, ne prend que des répertoires, pas des fichiers
    :param report_path : répertoire acceuillant les rapports
    :param registre: objet de métadonnées PREMIS
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
                extract_zipfile(old_path, filename, uncompliant_packs, exceeding_packs, user, registre)

            case ".tar":
                extract_tarfile(old_path, filename, uncompliant_packs, exceeding_packs, user, registre)

            case ".gz":
                extract_tarfile(old_path, filename, uncompliant_packs, exceeding_packs, user, registre)

            case ".7z":
                extract_7zfile(old_path, filename, uncompliant_packs, exceeding_packs, user, registre)
  
    if uncompliant_packs :
        filename = "uncompliant_packs.txt"
        file_path = os.path.join(report_path, filename)

        with open(file_path, "w+t", encoding="utf-8") as uncompliant_r:
            uncompliant_r.write("The following list contains uncompliant or problematic packs or files that were removed:")
            for pack in uncompliant_packs:
                uncompliant_r.write(f"\n{pack}")

        log_it("info",f"There are files or packages not compliant with your format policy.")
        log_it("info",f"You can check the list here : {file_path}")
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
        filename = "exceeding_packs.txt"
        file_path = os.path.join(report_path, filename)       
        with open(file_path, "w+t", encoding="utf-8") as uncompliant_r:
            uncompliant_r.write("Exceeding packs :")
            for pack in exceeding_packs:
                uncompliant_r.write(f"\n{pack}")


        log_it("info", f"There are also packages compliant with your format policy but that exceeds the authorized maximum size of 1 go or maximum number of files")
        log_it("info",f"You can check the list here : {file_path}")
        anwseer = input("May I remove them (yes/no)? :")
        while True:
            if anwseer == "yes":
                for pack in exceeding_packs:
                    remove_pack(pack)
                break
            elif answeer == "no":
                break


def extract_zipfile(old_path, file_n, uncomp_pack, exceed_pack, user, registre): 
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
            
            if stat.S_ISLNK(mode):
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
        log_it("info", f"New reposit created during dezip process {new_path}")

        try:
            zip.extractall(new_path)
            log_it("info", f"{old_path} extracted")
            event = Event(eventType="unpacking", eventDetail=f"Unpacked from : {old_path}", 
                          eventDateTime=horodatage(), eventOutcome="success")
            event.add_linking_agent(user)
            registre.add_event(event)
            remove_pack(old_path)

        except IOError as e:
            event = Event(eventType="unpacking", eventDetail=f"Not unpacked from : {old_path}", 
                          eventDateTime=horodatage(), eventOutcome="failure")
            event.add_linking_agent(user)
            registre.add_event(event)
            log_it("error", f"Unpacking failure. Detail : {e}" )
            pass


def extract_tarfile(old_path, file_n, uncomp_pack, exceed_pack, user, registre):
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

        try:
            tar.extractall(new_path, filter="data")
            log_it("info",f"{old_path} extracted") 
            event = Event(eventType="unpacking", eventDetail=f"Unpacked from : {old_path}", 
                          eventDateTime=horodatage(), eventOutcome="success")
            event.add_linking_agent(user)
            registre.add_event(event)
            remove_pack(old_path)

        except IOError as e:
            event = Event(eventType="unpacking", eventDetail=f"Not unpacked from : {old_path}", 
                          eventDateTime=horodatage(), eventOutcome="failure")
            event.add_linking_agent(user)
            registre.add_event(event)            
            log_it("error", f"Unpacking failure. Detail : {e}" )
            pass       


def extract_7zfile(old_path, file_n, uncomp_pack, exceed_pack, user, registre):
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

        try:        
            z.extractall(new_path)
            log_it("info",f"{old_path} extracted")
            registre.add_event(Event(eventType="unpacking", eventDetail=f"Unpacked from : {old_path}", eventDateTime=horodatage(), eventOutcome="success"))
            remove_pack(old_path)

        except IOError as e:
            registre.add_event(Event(eventType="unpacking", eventDetail=f"Not unpacked from : {old_path}", eventDateTime=horodatage(), eventOutcome="failure"))
            log_it("error", f"Unpacking failure. Detail : {e}" )
            pass

"""Analyse des formats avec DROID"""
def droid_check(source_path, reports, user, registre): 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    droid_path = os.path.join(base_dir, "droid", "droid.bat") #subprocess refuse les chemins relatifs

    if os.path.isfile(droid_path):
        try:
            log_it("info", "DROID has been launched, please note that that can take a few minutes...")
            result = subprocess.run([droid_path, "-a", source_path,"-Pr", "profile.generateHash=true", "hashAlgorithm=sha256", "-R"], 
                                    text=True, capture_output=True, check=True)
            write_report("droid_report.csv", reports, "droid", result)
            log_it("info", "DROID has successfully finished ! " \
            f"You can see the report into {reports}")
            event = Event(eventType="identification", eventDateTime=horodatage(), eventOutcome="success") 
            event.add_linking_agent(user)
            registre.add_event(event)

        except subprocess.CalledProcessError as e:
            event = Event(eventType="identification", eventDateTime=horodatage(), eventOutcome="failure")
            event.add_linking_agent(user)
            registre.add_event(event)
            log_it("error", f"DROID failed. Details : {e.stderr}, {e.stdout}")
            pass

    else :
        log_it("error","droid check has failed because droid.bat is not present on the Zenobie repository (droid/droid.bat). " \
        "Please install it and retry")


def assign_droid_data(copies_rep, reports, user, registre):
    """Assigne les métadonnées extraites via DROID aux objets de métadonnées"""
    droid_file_path = os.path.join(reports, "droid_report.csv")

    if os.path.isfile(droid_file_path):
        with open(droid_file_path, "r", encoding="utf-8", newline="") as f:
            writer = csv.DictReader(f, delimiter=",")
            for row in writer: 
                file_path = row["FILE_PATH"]
                rel_path = get_relative_path(file_path, copies_rep)
                droid_hash = row["HASH"]
                premis_object = get_premis_object(rel_path, droid_hash, registre)
                if premis_object is not None:
                    premis_object.formatName = row["FORMAT_NAME"]
                    premis_object.size = row["SIZE"]
                    premis_object.formatVersion = row["FORMAT_VERSION"]
                    premis_object.formatRegistryName = "PRONOM"
                    premis_object.formatRegistryKey = row["PUID"]
                    event = Event(eventType="identification", 
                                  eventDateTime=horodatage(), 
                                  eventDetail="program=DROID", 
                                  eventOutcome="success", 
                                  eventOutcomeDetailNote=f"{premis_object.formatRegistryKey}")
                   
                    # event.add_linking_object(premis_object)
                    event.add_linking_agent(user)
                    registre.add_event(event)
                    premis_object.add_linking_event(event)

    else:
        log_it("error", "Zenobie does not find the droid_report.csv file")   

def jhove_validation(source_path, reports, user, registre):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    jhove_path = os.path.join(base_dir, "jhove", "jhove.bat") #subprocess refuse les chemins relatifs
    if os.path.isfile(jhove_path):
        try:
            log_it("info", "JHOVE has been launched, please note that that can take a few minutes...")
            jhove_results = subprocess.run([jhove_path, source_path, "-k", "-h", "json"], 
                                           text=True, capture_output=True, check=True, encoding="utf-8")
            metadata = deserialize(jhove_results.stdout)
            write_json_report("jhove.json", reports, metadata)

            log_it("info", "JHOVE has successfully finished ! " \
            f"You can see the report into {reports}")  
            event = Event(eventType="validation", eventDateTime=horodatage(), eventOutcome="success")
            event.add_linking_agent(user)
            registre.add_event(event)
            

        except subprocess.CalledProcessError as e:
            event = Event(eventType="validation", eventDateTime=horodatage(), eventOutcome="failure")
            event.add_linking_agent(user)
            registre.add_event(event)
            log_it("error", f"JHOVE has failed {e.stderr}, {e.stdout}")
    else :
        event = Event(eventType="validation", eventDateTime=horodatage(), eventOutcome="failure")
        event.add_linking_agent(user)
        registre.add_event()
        log_it("error","JHOVE validation has failed because jhove.bat is not present on the Zenobie repository (jhove/jhove.bat). " \
        "Please install it and retry")

def assign_jhove_data(copies_rep, reports, user, registre):
    jhove_file_path = os.path.join(reports, "jhove.json")
    if os.path.isfile(jhove_file_path):
        jhove_dict_results = read_json_report("jhove.json", reports)
        jhove_version = jhove_dict_results["jhove"]["release"]
        for item in jhove_dict_results["jhove"]["repInfo"]:
            file_path = item["uri"]
            rel_path = get_relative_path(file_path, copies_rep)
            jhove_hash = item['properties'][3]['checksum'] #3 correspond au sha-256
            premis_object = get_premis_object(rel_path, jhove_hash, registre)
            if premis_object is not None :
                event = Event(eventType="validation", 
                    eventDateTime=horodatage(), 
                    eventDetail=f"program=JHOVE ; version={jhove_version}", 
                    eventOutcome="success", 
                    eventOutcomeDetailNote=f"format={item['format']}; version= {item['reportingModule']['release']}; result={item['status']}")
                    # event.add_linking_object(premis_object)
                event.add_linking_agent(user)
                registre.add_event(event)            
    else:
        log_it("error", "Zenobie does not find the jhove.json file") 


def remove_empty(copies_rep, report_r, user, registre):
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
    for root, _, files in os.walk(abs_path, topdown=False):
        try:
            if root == initial_root:
                continue
            if not os.listdir(root):
                os.chmod(root, stat.S_IWRITE)
                os.rmdir(root) 
                log_it("info",f"Removed: {root}")
                event = Event(eventType="deletion", eventDateTime=horodatage(), 
                              eventDetail=f"{root} was empty and has been removed")
                event.add_linking_agent(user)
                registre.add_event(event)
                removed += 1
        except Exception as e:
            log_it("error",f"Error on {root}: {e}")         
    log_it("info",f"Removing process done. Zenovie has removed {removed} empty repositories")

def remove_forbidden_chars(repository_path, report_r, user, registre):
    log_it("info", "launch of forbidden chars removing")
    #peut-être penser à mettre un dry run
    for root, _, files in os.walk(repository_path):
        for file in files:
            old_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file)
            old_name = get_relative_path(old_path, repository_path) 
            sha_256 = hash_calculator(old_path)
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
                new_name = get_relative_path(normalized_name, repository_path)
                premis_object = get_premis_object(old_name, sha_256, registre)
                if premis_object is not None:
                    premis_object.contentLocationValue = new_name
                    event = Event(eventType="filename change", eventDateTime=horodatage(), eventDetail=f"Original name: {old_name} - New name: {new_name}", eventOutcome="Success")
                    event.add_linking_agent(user)
                    registre.add_event(event)
                    premis_object.add_linking_event(event)

            except OSError as e:
                event = Event(eventType="filename change", eventDateTime=horodatage(), eventDetail=f"Zenobie failed to rename {old_path}: {e}", eventOutcome="failure")
                event.add_linking_agent(user)
                registre.add_event(event)
                continue

    write_report("rename_report.txt", report_r, type="rename", cible=registre)
    log_it("info", "removing of forbidden chars done")




def robo_copy(source: str, destination: str, log_repository: str, report_name: str, user, registre: PremisObjects) -> dict:
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    process = subprocess.run(["robocopy", source, destination,
                    "/e", "/copy:DATSO", "/X", "/V", "/FP", f"/log+:{log_repository}/{report_name}", "/TEE"], 
                    check=False) #/copyall changé en /copy:DATSO
    if process.returncode < 8 :
        log_it("info", "robocopy successful finished")
        event = Event(eventType="transfer", eventDateTime=horodatage(), 
        eventDetail= f"Robocopy process finished", eventOutcome="success")
        event.add_linking_agent(user)
        registre.add_event(event)        
        
    else:
        log_it("error", f"robocopy has encounter an error \nplease check the {log_repository}/{report_name} to fix it before retry the process")
        while True:
            try:
                answeer = str(input("Do you want to continue despite this problem (yes/no)? Answeer no will exit the script.")).lstrip().lower()
                if answeer == "yes":
                    log_it("info","Ok, we continue despite the problem")
                    break
                elif answeer == "no":
                    log_it("info","Ok, exiting the script because of robocopy problem")
                    sys.exit()
            except EmptyError:
                log_it("warning","Please, answeer by yes or no")

    paths_destination = get_relative_paths(destination) #utile pour la vérification avec les hashs
    return paths_destination

def finalizing_metadata(report_repository:str, registre:PremisObjects):
    write_report("events_report.txt", report_repository, type="event", cible=registre)
    write_report("objects.csv", report_repository, type="objects", cible=registre )
    write_json_report("objects.json", report_repository, registre.get_objects())
    log_it("info", "writing final objects.json")
