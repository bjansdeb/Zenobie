import os
import sys
import datetime

def main():
    user = str(input("Who are you : "))
    repository = str(input("What's the repository to audit : "))
    print(repository)
    if os.path.isdir(repository):
        state_of_art(repository, user)
    else:
        print("Path not correct")
    dezip()
    remove_empty()
    
"""Etat des lieux"""
def state_of_art(rep, us):
    start_depth = 1
    count = 0
    state_report = open("state_report.txt", "w+t")
    full_size = os.path.getsize(str(rep)) #taille du contenu de la totalité du répertoire en bytes
    date = datetime.datetime.now() #horodatage du rapport
    for root, dirs, files in os.walk(rep):
        current_depth = root.replace(rep, '').count(os.sep) #compte la profondeur à partir du répertoire actuel moins la racine
        max_depth = max(start_depth, current_depth) #calcule la différence entre le niveau 1 et le compte des profondeurs

    print(f"Audit of {rep}")
    print("Size of the repository", full_size + " bytes")    
    print("Max-depth:", max_depth)
    print(f"Report done with Zenobie at {date}")
    state_report.write(f"Audit of {rep}")
    state_report.write(f"\nSize of the repository" + full_size + " bytes")
    state_report.write(f"\nMax-depth: {max_depth}")
    state_report.write(f"\nReport done with Zenobie at {date} by {us}")

"""Décompression des fichiers"""
def dezip():
    ...

"""Suppression de dossiers vides"""
def remove_empty():
    ...



if __name__ == "__main__":
    main()