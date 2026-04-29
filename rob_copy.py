from pathlib import Path
import subprocess
import os

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
            print('path does not exist. Please retry')
            continue
    
    while True:
        try:
            destination = fr'{str(input("Path destination (f.i. : C:/archives/):"))}'
            if not os.path.exists(destination):
                raise ValueError
            else:
                break
        except ValueError:
            print('path does not exist. Please retry')
            continue

    while True:
        try:
            log_repository = fr'{str(input("Path report (f.i. : C:/archives/):"))}'
            if not os.path.exists(log_repository):
                raise ValueError
            else:
                break
        except ValueError:
            print('path does not exist. Please retry')
            continue

    robot_copy(source, destination, log_repository)


def robot_copy(source: str, destination: str, log_repository: str):
    paths_source = get_relative_path(source)
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/E", "/copy:DATSO", f"/log+:{log_repository}/transfert_report.txt", "/X", "/V", "/FP", "/TEE"], #copy_all changé en DASTO
                    check=False)
    paths_destination = get_relative_path(destination)
    #compare_files()

def get_relative_path(source : str) -> dict:
    paths_array = { }
    path = os.walk(source)
    for root, _, files in path :
        for file in files:
            filename = os.path.join(root, file)
            p = Path(filename)
            source_p = Path(fr'{source}')
            paths_array[file] = source_p.name / p.relative_to(source_p)
    return paths_array

def compare_files(paths_source, paths_destination, root_source, root_destination):
    print("root source", root_source)
    source_path = Path(fr'{root_source}') #absolu /robo_copy


    for file in paths_source:
        p = Path(paths_source[file])
        print("relative root:", p.relative_to(source_path))
        # print(path, paths_source[path])

    #à faire : récolter tous les relatifs sources dans un dict ; récolter tous les relatifs dest dans un dict
    #comparer hash source avec hash dest, rel source avec rel dest
    #si ok, sur base de rel dest, aller chercher object avec path path dest correspondant et adapter celui-ci dans métadonnées
    #prévoir un clear des objets dict /sauvegarde dans json

    #réflexion additionnelle : enregistrer les chemins relatifs dans les métadonnées objects ; permet de sortir du problème physique - abstrait
    #car le relatif ne changera plus vraiment


if __name__ == "__main__":
    main()