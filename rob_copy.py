import subprocess
import os

def main() :
    print("process launched")
    source = str(input("Path source:"))
    destination = str(input("Path destination:"))
    log_repository = str(input("Path report :"))

    robot_copy(source, destination, log_repository)


def robot_copy(source, destination, log_repository):
    print(source)
    get_path(source)
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/E", "/copy:DATSO", f"/log+:{log_repository}/transfert_report.txt", "/X", "/V", "/FP", "/TEE"], #copy_all changé en DASTO
                    check=False)
    get_path(destination)
    print(destination)
    compare_files(source, destination)

def get_path(source):
    path = os.walk(source)
    for root, dirs, files in path :
        print(root, dirs, files)
        for file in files:
            filename = os.path.join(root, file)
            print("file:", file)
            print(filename)
            
def compare_files(source, destination):
    ...

if __name__ == "__main__":
    main()