from pathlib import PurePath, PureWindowsPath, Path
import subprocess
import os

def main() :
    print("process launched")
    source = str(input("Path source:"))
    destination = str(input("Path destination:"))
    log_repository = str(input("Path report :"))

    robot_copy(source, destination, log_repository)


def robot_copy(source, destination, log_repository):
    # print(source)
    root_source = source
    root_destination = destination
    paths_source = get_path(source)
    # subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    # subprocess.run(["robocopy", source, destination, 
    #                 "/E", "/copy:DATSO", f"/log+:{log_repository}/transfert_report.txt", "/X", "/V", "/FP", "/TEE"], #copy_all changé en DASTO
    #                 check=False)
    paths_destination = get_path(destination)


    compare_files(paths_source, paths_destination, root_source, root_destination)

def get_path(source):
    paths_array = { }
    path = os.walk(source)
    for root, dirs, files in path :
        # print(root, dirs, files)
        for file in files:
            filename = os.path.join(root, file)
            paths_array[file] = filename
    return paths_array

def compare_files(paths_source, paths_destination, root_source, root_destination):
    print("root source", root_source)
    source_path = Path(fr'{root_source}') #absolu /robo_copy
    
    r = Path('C:/Users/BenjaminJanssensdeBi/OneDrive - Archief- en Onderzoekscentrum voor Vrouwengeschiedenis/Desktop/Développement/Zenobie/robocopy')
    c = Path('C:/Users/BenjaminJanssensdeBi/OneDrive - Archief- en Onderzoekscentrum voor Vrouwengeschiedenis/Desktop/Développement/Zenobie/robocopy/Refleks_bernard.xlsx')
    rel = c.relative_to(r)


    for file in paths_source:
        p = Path(paths_source[file])
        print("relative root:", p.relative_to(source_path))
        # print(path, paths_source[path])

    #à faire : récolter tous les relatifs sources dans un dict ; récolter tous les relatifs dest dans un dict
    #comparer hash source avec hash dest, rel source avec rel dest
    #si ok, sur base de rel dest, aller chercher object avec path path dest correspondant et adapter celui-ci dans métadonnées
    #prévoir un clear des objets dict /sauvegarde dans json
if __name__ == "__main__":
    main()