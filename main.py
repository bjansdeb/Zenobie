import os
import sys
import time

from config import read_config
from errors import EmptyError
from log import log_it
from models import Agent, Mets, PremisObjects
from util import (assign_droid_data, assign_jhove_data,
                  create_bay, create_objects, droid_check,
                  dezip, finalizing_metadata, horodatage, 
                  jhove_validation, 
                  remove_empty, remove_forbidden_chars,
                  sail_to_bay, state_of_art, size_name_check)


config_data = read_config()
MEDIAN_PATH_SIZE = int(config_data['median_path'])
MAX_PATH_SIZE = int(config_data['max_path'])

def main():
    
    log_it("info", "Welcome, my name is Zenobie and I'm going to help you to deal your digital bulk")
    name = str(input("What's your name : "))
    role = str(input(f"Hello {name}. What's your role at Carhif: "))
    user = Agent (agentName=name, agentType=None, note=role)
    mets = Mets(hdr_create_date=horodatage(), hdr_id_producter="A1")
    registry = PremisObjects()
    source_repository, originals_repository, copies_repository, project_name  = "", "", "", ""


    while True:
        source_repository = str(input("Super ! Ok let's work, what's the path to your digital bulk repository :").strip())
        try:
            if len(source_repository) >= MEDIAN_PATH_SIZE :
                log_it("warning", "The indicated path has a length equal or higher than 200 chars. Please, note the maximum path length for Windows is 260 chars." \
                "This length may crash the script\n")
                time.sleep(3)
            if not os.path.exists(source_repository):
                log_it("warning", "The indicated path does not exist.")
                continue
            if not os.path.isdir(source_repository):
                log_it("warning", "The indicated path is not a directory.")
                continue

            project_name = os.path.basename(os.path.normpath(source_repository))
            break
        except IsADirectoryError:
            raise IsADirectoryError("Repertory nod valid, retry with a correct path name")        
        except NotADirectoryError: 
            raise NotADirectoryError("Please select a directory and retry")
        except ValueError:
            raise ValueError("Repertory not valid, retry") 
        except FileNotFoundError:
            raise FileNotFoundError("The indicated path is not correct, retry")

    while True:
        try:
            higher_name = size_name_check(source_repository)

            if higher_name >= MAX_PATH_SIZE:
                log_it("warning", f"The higher pathname inside the given repository has a length of {higher_name} chars. Please, note the maximum pathname length for Windows is 260 chars." \
                        "This length may crash the script\n")
                
                answer = str(input("Do you want to continue anyway(yes/no)? If no, you will leave the program")).lstrip().lower()
                if answer == "yes":
                    log_it("info","Ok, we continue despite too high pathname")
                    time.sleep(3)
                    break
                elif answer == "no":
                    log_it("info","Ok, you are leaving Zenobie. Bye!")
                    time.sleep(2)
                    sys.exit()
                else :
                    raise EmptyError   
            else:
                break
        except EmptyError:
            log_it("warning","Please, answer by yes or no")



    project_paths = create_bay(project_name) #création des dossiers de la baie d'arrivage si n'existent pas  
    originals_repository = project_paths['originals']
    copies_repository = project_paths['copies']
    reports_repository = project_paths['reports']

    if os.path.isdir(source_repository):
        create_objects(source_repository, reports_repository, user, registry)    
        sail_to_bay(source_repository, originals_repository, 
                    copies_repository, reports_repository, user, registry)
    if os.path.isdir(copies_repository):
        state_of_art(source_repository, reports_repository, user, registry)
    else :
        log_it("warning","Path not correct, retry please")
        pass


    log_it("Info", "Dezipping compressed directories...")
    time.sleep(2)
    dezip(copies_repository, reports_repository, user, registry)


    while True:
        try:
            answer = str(input("May I scan and remove empty repositories(yes/no)?")).lstrip().lower()
            if answer == "yes":
                remove_empty(copies_repository, reports_repository, user, registry)
                break
            elif answer == "no":
                log_it("info","Ok, we continue without removing the empty repositories")
                time.sleep(2)
                break
        except EmptyError:
            log_it("warning","Please, answer by yes or no ")

    while True:
        try: 
            answer = str(input("Ok, now let's take a look to the forbidden chars. May I scan and removing them (yes/no)?")).lstrip().lower()
            if answer == "yes":
                remove_forbidden_chars(copies_repository, reports_repository, user, registry)
                break
            elif answer == "no":
                log_it("info","Ok, we continue without removing the forbidden chars")
                time.sleep(2)                
                break                    
        except EmptyError:
            log_it("warning","Please, answer by yes or no ")  

    log_it("info", "The process is almost finished. We are going to look to the formats used in this directrory with DROID. " \
    "Please, note that some formats may be forbidden by our formats policy")
    time.sleep(2)
    droid_check(copies_repository, reports_repository, user, registry)
    assign_droid_data(copies_repository, reports_repository, user, registry)
    jhove_validation(copies_repository, reports_repository, user, registry)
    assign_jhove_data(copies_repository, reports_repository, user, registry)
    finalizing_metadata(reports_repository, registry)

    log_it("warning", f"Process successfully finished {user.agentName}, bye !")

if __name__ == "__main__":
    main()