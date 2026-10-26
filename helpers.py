import datetime
import hashlib
import json
import os

from log import log_it
from models import Event, PremisObjects
from pathlib import Path

"""-----------------------------------------------"""
"""            **** Functions secondaires  ****   """
"""-----------------------------------------------"""

def hash_calculator(source):
    sha_256 = hashlib.sha256()
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            sha_256.update(chunk)
    return sha_256.hexdigest()

def verify_hashs_and_paths(paths_destination: dict, registre: PremisObjects) ->dict:
    """ Vérifie les hashs et les chemins récoltés dans paths_destination avec les chemins et hash contenus dans les objets de métadonnées"""
    log_it("info", "lauching hashs and paths verification")
    integrity_problems = {}
    obj_relative_paths = {}
    
    for obj in registre.objects.values():
        obj_relative_paths[obj.contentLocationValue] = obj.messageDigest

    for rel_path in paths_destination:
        if rel_path in obj_relative_paths.keys():
            if paths_destination[rel_path][0] == obj_relative_paths.get(rel_path):
                event = Event(eventType="transfer", eventOutcome="success", eventDetail=f"{obj_relative_paths.get(rel_path)} succesfully transfered to {paths_destination[rel_path][1]}", eventDateTime=horodatage())
                registre.add_event(event)
                continue
            else :
                integrity_problems[paths_destination[rel_path]] = f"Hash {paths_destination[rel_path][0]} does not match any path in the source repository"
                event = Event(eventType="transfer", eventOutcome="failure", eventDetail=f"{obj_relative_paths.get(rel_path)} not transfered to {paths_destination[rel_path][1]}", eventDateTime=horodatage())
                registre.add_event(event)
        else:
            integrity_problems[paths_destination[rel_path]] = f"{rel_path} has not equivalent path in the source repository"
    
    log_it("info", "hashs and paths verification done")

    return integrity_problems     

def get_premis_object(rel_path:str, hash_value:str, registre: PremisObjects) ->PremisObjects:
    for object in registre.objects.values():
        if rel_path in object.contentLocationValue :
            if hash_value == object.messageDigest:
                return object
            else:
                continue

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
    """
    Utilisé pour vérifier que les nouveaux noms de fichiers ne rentrent pas en collision avec des noms précédents
    """
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


def is_safe_path(base_dir: Path, requested_path: str) -> bool:
    #https://medium.com/@contactomyna/securing-zip-file-operations-understanding-and-preventing-path-traversal-attacks-74d79f696c46
    """S'assure que les opérations se passent dans le bon fichier"""
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
    path = str(parent.name / child.relative_to(parent)) #.as_posix()
    return path #.as_posix()

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
            rel_path = str(source_p.name / p.relative_to(source_p)) #as_posix
            paths_array[rel_path] = (hash_output, filename)
    return paths_array

def serialize(json_file):
    return json.dumps(json_file, indent=4)

def deserialize(json_file):
    return json.loads(json_file)