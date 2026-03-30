import subprocess

def main() :
    print("process launched")
    source = str(input("Path source:"))
    destination = str(input("Path destination:"))
    log_repository = str(input("Path report :"))

    robot_copy(source, destination, log_repository)


def robot_copy(source, destination, log_repository):
    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/e", "/copyall", f"/log+:{log_repository}/transfert_report.txt"], 
                    check=False)
    

if __name__ == "__main__":
    main()