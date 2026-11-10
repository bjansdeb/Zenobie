import os
import sys
import time
from errors import EmptyError
from log import log_it
from models import Agent, Event, Object, Mets, PremisObjects, State
from reporting import write_report
from util import *

def main():
    
    log_it("info", "Welcome, my name is Zenobie and I'm going to help you to deal your digital bulk")
    name = str(input("What's your name : "))
    role = str(input(f"Hello {name}. What's your role at Carhif: "))
    user = Agent (agentName=name, agentType=None, note=role)
    mets = Mets(hdr_create_date=horodatage(), hdr_id_producter="A1")
    registre = PremisObjects()
    repository, originals_repository, copies_repository, project_name  = "", "", "", ""


    while True:
        repository = str(input("Super ! Ok let's work, what's the path to your digital bulk repository :"))
        try:
            if len(repository) >= 200 :
                log_it("warning", "The given path has a length equal or higher than 200 chars. Please, note the maximum path length for Windows is 260 chars." \
                "This length may crash the script\n")
                time.sleep(3)

            project_name = os.path.basename(repository)
            break
        except IsADirectoryError:
            raise("Repertory nod valid, retry with a correct path name")        
        except NotADirectoryError: 
            raise("Please select a directory and retry")
        except ValueError:
            raise ("Repertory not valid, retry") 
        except FileNotFoundError:
            raise("The indicated path is not correct, retry")

    while True:
        try:
            higher_name = size_name_check(repository)

            if higher_name >= 240:
                log_it("warning", f"The higher pathname inside the given repository has a length of {higher_name} chars. Please, note the maximum pathname length for Windows is 260 chars." \
                        "This length may crash the script\n")
                
                answeer = str(input("Do you want to continue anyway(yes/no)? If no, you will leave the program")).lstrip().lower()
                if answeer == "yes":
                    log_it("info","Ok, we continue despite too high pathname")
                    time.sleep(3)
                    break
                elif answeer == "no":
                    log_it("info","Ok, you are leaving Zenobie. Bye!")
                    time.sleep(2)
                    sys.exit()
                else :
                    raise EmptyError   
            else:
                break
        except EmptyError:
            log_it("warning","Please, answeer by yes or no")



    project_paths = create_bay(project_name) #création des dossiers de la baie d'arrivage si n'existent pas  
    originals_repository = project_paths['originals']
    copies_repository = project_paths['copies']
    reports = project_paths['reports']

    if os.path.isdir(repository):
        create_objects(repository, reports, user, registre)
    
    if os.path.isdir(repository):
        sail_to_bay(repository, originals_repository, 
                    copies_repository, reports, user, registre) 
    if os.path.isdir(copies_repository):
        state_of_art(repository, reports, user, registre)
    else :
        log_it("warning","Path not correct, retry please")
        pass


    log_it("Info", "Dezipping compressed directories...")
    time.sleep(2)
    dezip(copies_repository, reports, user, registre)


    while True:
        try:
            answeer = str(input("May I scan and remove empty repositories(yes/no)?")).lstrip().lower()
            if answeer == "yes":
                remove_empty(copies_repository, reports, user, registre)
                break
            elif answeer == "no":
                log_it("info","Ok, we continue without removing the empty repositories")
                time.sleep(2)
                break
        except EmptyError:
            log_it("warning","Please, answeer by yes or no ")

    while True:
        try: 
            answeer = str(input("Ok, now let's take a look to the forbidden chars. May I scan and removing them (yes/no)?")).lstrip().lower()
            if answeer == "yes":
                remove_forbidden_chars(copies_repository, reports, user, registre)
                break
            elif answeer == "no":
                log_it("info","Ok, we continue without removing the forbidden chars")
                time.sleep(2)                
                break                    
        except EmptyError:
            log_it("warning","Please, answeer by yes or no ")  

    log_it("info", "The process is almost finished. We are going to look to the formats used in this directrory with DROID. " \
    "Please, note that some formats may be forbidden by our formats policy")
    time.sleep(2)
    droid_check(copies_repository, reports, user, registre)
    assign_droid_data(copies_repository, reports, user, registre)
    jhove_validation(copies_repository, reports, user, registre)
    assign_jhove_data(copies_repository, reports, user, registre)
    finalizing_metadata(reports, registre)

    while True:
        try:
            input(f"Process successfully finished {user.agentName}, do ctrl+c to quit the program")
            if sys.exit():
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            print("\nscript closed")
            sys.exit()

if __name__ == "__main__":
    main()