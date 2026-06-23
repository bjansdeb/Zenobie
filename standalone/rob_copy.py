from pathlib import Path
import datetime
import hashlib
import os
import subprocess
import time
import uuid


def main() :
    print("Robocopy launched")
    time.sleep(1)
    print("Note : you may quit the script at any time doing crtl+c")
    time.sleep(3)
    user = ""
    role = ""

    while True : 
        try:
            user = str(input("Hello buddy, what's your name ? :"))
            if user == "":
                raise ValueError
            else :
                break

        except ValueError:
            pass

    while True:
        try: 
            role = str(input(f"Super {user}. Now what's your role at Carhif (archivist, librarian...): "))
            if role == "":
                raise ValueError
            else :
                print("Ok, so you are an", role)
                time.sleep(2)
                break

        except ValueError:
            pass

    while True :    
        try:
            source = fr'{str(input("Path source (repository you want to copy. For instance : C:/archives/refleks):"))}'
            if not os.path.exists(source):
                raise ValueError
            else:
                break

        except ValueError:
            print('This path does not exist. Please retry')
            pass

        except NameError:
            print('This path is the same as the source path. Please retry with another path')
            pass   

    while True:
        try:
            print("----\n")
            print("\nOk, now it's time to define your destination repository")
            print("\n/!\ for this step: the destination repository must have the same name than the original one (f.i. C:/refleks -> D:/archives/refleks)")
            destination = fr'{str(input("Repository where to move your copy, f.i. : C:/archives/destination/refleks):"))}'
            if not os.path.exists(destination):
                raise ValueError
            elif destination == source:
                raise NameError
            else:
                break

        except ValueError:
            print('This path does not exist. Please retry')
            pass
 
        except NameError:
            print('This path is the same as the source path. Please retry with another path')
            pass

    while True:
        try:
            log_repository = fr'{str(input("Path report (repository where to put your reports, f.i. : C:/archives/report):"))}'
            if not os.path.exists(log_repository):
                raise ValueError
            elif log_repository == source or log_repository== destination:
                raise NameError
            else:
                break
        except ValueError:
            print('This path does not exist. Please retry')
            pass

        except NameError:
            print('This path is the same as the source or the destination path. Please retry with another path')
            pass    

    robo_copy(source, destination, log_repository, user, role)
    

    print("Process done, you may quit doinc crtl+c. The script will automatically close in 50 seconds")
    time.sleep(40)

def robo_copy(source: str, destination: str, log_repository: str, user: str, role: str):
    """ Copy source to destination. Include integrity check with hash and paths"""

    subprocess.run("chcp 65001", shell=True) #utilisé pour ajouter les caractères spéciaux fr avant le run de robotcopy
    subprocess.run(["robocopy", source, destination, 
                    "/E", "/copy:DATS", f"/log+:{log_repository}/transfert_report.txt", "/X", "/V", "/FP", "/TEE"], #copy_all changé en DASTO puis DATS à cause NFTS
                    check=False)
    
    paths_source = get_relative_paths(source, log_repository, user, role)    
    paths_destination = get_relative_paths(destination, log_repository, user, role)
    integrity_problems = verify_hashs_and_paths(paths_source, paths_destination, log_repository, user, role)

    if integrity_problems:
        integrity_path = os.path.join(log_repository, "integrity_problems.txt")
        with open(integrity_path, "w+t", encoding="utf-8") as integrity_r:
            integrity_r.write("-------------")       
            integrity_r.write(f"\nIntegrity report")
            integrity_r.write(f"\nDone at {horodatage()} by {user}, {role} at AVG-Carhif using Python 3.10")  
            for problems in integrity_problems:            
                integrity_r.write(f"\n{problems}")
        while True:
            try:
                time.sleep(1)
                print(f"{user}, there are some integrity problems. Check {integrity_path} and try to fix it before retry")
                print("process done, crtl + c to exit")
            except KeyboardInterrupt:
                pass

def get_relative_paths(source : str, log_repository: str, user: str, role: str) -> dict:
    paths_array = {}

    report_path = os.path.join(log_repository, "hashs_report.txt")
    with open(report_path,"w+t", encoding="utf-8") as hash_r:
        hash_r.write("-------------")       
        hash_r.write(f"\nHash report")
        hash_r.write(f"\nDone at {horodatage()} by {user}, {role} at AVG-Carhif using Python 3.10")       
   
        path = os.walk(source)
        for root, _, files in path :
            for file in files:
                filename = os.path.join(root, file)
                p = Path(filename)
                source_p = Path(fr'{source}')
                hash_output = hash_calculator(filename)
                hash_r.write(f"\n--------")  
                hash_r.write(f"\nEvent id type: digital signature generation")
                hash_r.write(f"\nEvent id: {uuid.uuid1().hex}")
                hash_r.write(f"\nEvent date time: {horodatage()}")        
                hash_r.write(f"\nEvent outcome: success") 
                hash_r.write(f"\nEvent detail: {filename} get the sha256 hash {hash_output}")  

                rel_path =  str(source_p.name / p.relative_to(source_p))
                paths_array[rel_path] = (hash_output, filename)
    
    return paths_array

def verify_hashs_and_paths(paths_source: dict, paths_destination: dict, log_repository: str, user: str, role: str) -> dict:
    print("Verifying the transfert with hashs and paths...")
    time.sleep(2)
    integrity_problems = {}

    report_path = os.path.join(log_repository, "transert_detail.txt")
    with open(report_path, "w+t", encoding="utf-8") as transf_r:
        transf_r.write("-----------")
        transf_r.write(f"\nTransfert report")
        transf_r.write(f"\nDone at {horodatage()} by {user}, {role} at AVG-Carhif using Python 3.10 and Robocopy")


        for rel_path in paths_destination.keys():
            if rel_path in paths_source.keys():
                if paths_destination[rel_path][0] == paths_source[rel_path][0]:
                    transf_r.write(f"\n--------") 
                    transf_r.write(f"\nEvent id type: transfer")
                    transf_r.write(f"\nEvent id: {uuid.uuid1().hex}")
                    transf_r.write(f"\nEvent date time: {horodatage()}")
                    transf_r.write(f"\nEvent outcome: success")
                    transf_r.write(f"\nEvent detail: {paths_source[rel_path][1]} succesfully transfered to {paths_destination[rel_path][1]}")
                    continue
                else :
                    integrity_problems[paths_destination[rel_path]] = f"Hash {paths_destination[rel_path][0]} does not match any path in the source repository"
                    transf_r.write(f"\n--------") 
                    transf_r.write(f"\nEvent id type: transfer")
                    transf_r.write(f"\nEvent id: {uuid.uuid1().hex}")
                    transf_r.write(f"\nEvent date time: {horodatage()}")
                    transf_r.write(f"\nEvent outcome: failure")
                    transf_r.write(f"\nEvent detail: {paths_source[rel_path][1]} not transfered to {paths_destination[rel_path][1]}")
            else :
                integrity_problems[paths_destination[rel_path]] = f"{rel_path} has not equivalent path in the source repository"

    return integrity_problems

def hash_calculator(source):
    sha = hashlib.sha256()
    #print(source)
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')


if __name__ == "__main__":
    main()