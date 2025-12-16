import os
import sys
from errors import EmptyError
from models import Agent, Event, Object, Report, Mets, State
from util import create_bay, create_objects, sail_to_bay, state_of_art, dezip, droid_check, remove_empty, remove_forbidden_chars, write_report, horodatage

#os.utime() report

def main():
    
    print("Welcome, my name is Zenobie and I'm going to help you to deal your digital bulk")
    name = str(input("What's your name : "))
    role = str(input(f"Hello {name}. What's your role at Carhif: "))
    user = Agent (name, "UUID", agentType=None, note=role)
    mets = Mets (hdr_create_date=horodatage(), hdr_id_producter="A1")
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

    originals_repository, copies_repository, unload_bay, reports = create_bay(user, project_name, mets)  #création des dossiers de la baie d'arrivage si n'existent pas    
    if os.path.isdir(repository):
        create_objects(repository, reports, user, mets)
    
    if os.path.isdir(repository):
        sail_to_bay(repository, originals_repository, 
                    copies_repository, unload_bay, reports, user, mets) #la fonction retourne le répertoire des copies sur lequel va se faire le state of art
    if os.path.isdir(copies_repository):
        state_of_art(repository, reports, user, mets)
        while True:
            try:
                answeer = str(input("May I dezip repositories(yes/no)?")).lstrip().lower()
                if answeer == "yes":
                    dezip(copies_repository, mets)
                    break
                elif answeer == "no":
                    print("ok, we continue without dezipping repositories")
                    break
                else :
                    raise EmptyError            
            except EmptyError:
                print("Please, answeer yes or no")
                
        #remove_empty(copies_repository, mets) #s'en occuper plus tard, nécessite de lui préciser de continuer si le répertoire n'est pas vide
        remove_forbidden_chars(copies_repository, reports, mets)
        droid_check(repository, mets)
        write_report("events_report.txt", reports, type="event", cible=mets)
        while True:
            try:
                input(f"Process successfully finished {user.agentName}, do ctrl+c to quit the program")
                if sys.exit():
                    raise KeyboardInterrupt
            except KeyboardInterrupt:
                print("script closed")
                sys.exit()
    else :
        print("Path not correct, retry please")
        pass



if __name__ == "__main__":
    main()