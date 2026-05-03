from pathlib import Path
import hashlib
import json
import os
import subprocess


def main() :
    print("process launched")

    while True : 
        try:
            source = fr'{str(input("Path source (for instance : C:/archives/):"))}'
            if not os.path.exists(source):
                raise ValueError
            else:
                break
        except ValueError:
            print('This path does not exist. Please retry')
            continue
        except NameError:
            print('This path is the same as the source path. Please retry with another path')   

    while True:
        try:
            destination = fr'{str(input("Path destination (f.i. : C:/archives/):"))}'
            if not os.path.exists(destination):
                raise ValueError
            elif destination == source:
                raise NameError
            else:
                break
        except ValueError:
            print('This path does not exist. Please retry')
            continue
        except NameError:
            print('This path is the same as the source path. Please retry with another path')

    while True:
        try:
            log_repository = fr'{str(input("Path report (f.i. : C:/archives/):"))}'
            if not os.path.exists(log_repository):
                raise ValueError
            elif log_repository == source or log_repository== destination:
                raise NameError
            else:
                break
        except ValueError:
            print('This path does not exist. Please retry')
            continue
        except NameError:
            print('This path is the same as the source or the destination path. Please retry with another path')    

    robo_copy(source, destination, log_repository)

def robo_copy(source: str, destination: str, log_repository: str):
    """ Copy source to destination. Include integrity check with hash and paths"""

    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/E", "/copy:DATSO", f"/log+:{log_repository}/transfert_report.txt", "/X", "/V", "/FP", "/TEE"], #copy_all changé en DASTO
                    check=False)
    
    paths_source = get_relative_paths(source)    
    paths_destination = get_relative_paths(destination)
    verify_hashs_and_paths(paths_source, paths_destination)

def get_relative_paths(source : str) -> dict:
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

def verify_hashs_and_paths(paths_source: dict, paths_destination: dict, log_repository: str = None):
    integrity_problems ={}

    for p in paths_destination:
        if p in paths_source:
            if paths_destination[p] == paths_source[p]:
                continue
            else :
                integrity_problems[paths_destination[p]] = f"Hash {paths_destination[p]} does not match any path in the source repository"
        else :
            integrity_problems[paths_destination[p]] = f"{p} has not equivalent path in the source repository"
    
    if integrity_problems:
        print("integrity problems", integrity_problems)
        return integrity_problems

    else:
        print("integrity check done without problems")
        # p = Path(paths_source[file])
        # print("relative root:", p.relative_to(source_path))
        # # print(path, paths_source[path])

    #à faire : récolter tous les relatifs sources dans un dict ; récolter tous les relatifs dest dans un dict
    #comparer hash source avec hash dest, rel source avec rel dest
    #si ok, sur base de rel dest, aller chercher object avec path path dest correspondant et adapter celui-ci dans métadonnées
    #prévoir un clear des objets dict /sauvegarde dans json

    #réflexion additionnelle : enregistrer les chemins relatifs dans les métadonnées objects ; permet de sortir du problème physique - abstrait
    #car le relatif ne changera plus vraiment


def hash_calculator(source):
    md5 = hashlib.md5()
    #print(source)
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

def serialize(object):
    return json.dumps(object)

def deserialize(json_file):
    return json.loads(json_file)

if __name__ == "__main__":
    main()