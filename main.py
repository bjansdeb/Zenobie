import os
import sys
from errors import EmptyError
from log import log_it
from models import Agent, Event, Object, Report, Mets, PremisObjects, State
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


    originals_repository, copies_repository, unload_bay, reports = create_bay(user, project_name, registre)  #création des dossiers de la baie d'arrivage si n'existent pas    
    if os.path.isdir(repository):
        create_objects(repository, reports, user, registre)
    
    if os.path.isdir(repository):
        sail_to_bay(repository, originals_repository, 
                    copies_repository, unload_bay, reports, user, registre) #la fonction retourne le répertoire des copies sur lequel va se faire le state of art
    if os.path.isdir(copies_repository):
        state_of_art(repository, reports, user, registre)
    else :
        log_it("warning","Path not correct, retry please")
        pass

    while True:
        try:
            answeer = str(input("May I dezip repositories(yes/no)?")).lstrip().lower()
            if answeer == "yes":
                dezip(copies_repository, registre)
                break
            elif answeer == "no":
                log_it("info", "ok, we continue without dezipping repositories")
                break
            else :
                raise EmptyError            
        except EmptyError:
            log_it("warnin","Please, answeer by yes or no")

    while True:
        try:
            answeer = str(input("May I scan and remove empty repositories(yes/no)?")).lstrip().lower()
            if answeer == "yes":
                remove_empty(copies_repository, reports, registre)
                break
            elif answeer == "no":
                log_it("info","Ok, we continue without removing the empty repositories")
                break
        except EmptyError:
            log_it("warning","Please, answeer by yes or no ")

    while True:
        try: 
            answeer = str(input("Ok, now let's take a look to the forbidden chars. May I scan and removing them (yes/no)?")).lstrip().lower()
            if answeer == "yes":
                remove_forbidden_chars(copies_repository, reports, registre)
                break
            elif answeer == "no":
                log_it("info","Ok, we continue without removing the forbidden chars")
                break                    
        except EmptyError:
            log_it("warning","Please, answeer by yes or no ")  

    log_it("info", "The process is almost finished. We are going looking to the formats used in this directrory with DROID. " \
    "Please, not that some formats are forbidden by your formats policy")
    droid_check(copies_repository, reports, registre)
    write_report("events_report.txt", reports, type="event", cible=registre)
    
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