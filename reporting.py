import csv
import os
import json

from log import log_it
from helpers import serialize, deserialize



def write_report(file_name: str, report_path: str, type: str, cible: object = None, dict_cible: dict = None):
    """
    Function d'écriture des rapports
    :param file_name: Nom du fichier
    :param report_path: Répertoire où va être placé le rapport
    :param type: hash, state, event, transfer, rename, integrity, unmatched_hash
    :param cible: Objet sur lequel porte le rapport
    :parem dict_cible : Dict sur lequel porte le rapport
    """
    file_path = os.path.join(report_path, file_name)
    match type:
        case "droid":
            with open(file_path, "w", encoding="utf-8") as droid_r:
                droid_r.write(f"{cible.stdout}")
        
        case "hash":
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_name', 'hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for object in cible.objects.values() :
                    writer.writerow({'object_name': {object.contentLocationValue}, 'hash': {object.messageDigest}})
            log_it("info",f"Hash report done, see {file_path}")

        case "integrity":
            with open(file_path, "w+t", encoding="utf-8") as integrity_r:
                integrity_r.write("-------------")       
                integrity_r.write(f"\nIntegrity report")
                for problems in dict_cible:            
                    integrity_r.write(f"\n{problems}")          
        
        case "unmatched_hash":
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_name', 'hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for object in cible.objects.values() :
                    writer.writerow({'object_name': {object.contentLocationValue}, 'hash': {object.messageDigest}})
            log_it("info",f"Hash report done, see {file_path}")            


        case "state":           
            with open(file_path, "w+t", encoding="utf-8") as state_r:
                state_r.write(f"Audit of {cible.title}")
                state_r.write(f"\nSize of the repository :{cible.full_size} bytes")
                state_r.write(f"\nMax-depth: {cible.depth}")
                state_r.write(f"\nNumber of files : {cible.files_number}")
                state_r.write(f"\nNumber of repositories : {cible.repositories_number}")
                state_r.write("\n*Please, note that the indicated dates depend on the operating system and may considerably changed from a system to another*")
                state_r.write(f"\nOldest created file : {cible.oldest_created_file} at {cible.oldest_created_time}")
                state_r.write(f"\nMost recent created file : {cible.most_recent_created_file} at {cible.most_recent_created_time}")
                state_r.write(f"\nOldest modified file : {cible.oldest_modified_file} at {cible.oldest_modified_time}")
                state_r.write(f"\nMost recent modified file : {cible.most_recent_modified_file} at {cible.most_recent_modified_time}")
                if cible.extensions is not None :
                    state_r.write(f"\nExtensions :")
                    for extension in cible.extensions : 
                        state_r.write(f"{extension} ;")
                state_r.write(f"\nReport done with Zenobie at {cible.date} by {cible.author} ({cible.role})")
                state_r.write(f"\nContent:")
                for path, content in cible.list_dir.items():
                    state_r.write(f"\n {path}\n")

                    for d in content["dirs"]:
                        state_r.write(f"   |── {d}/\n")

                    for f in content["files"]:
                        state_r.write(f"   |── {f}\n")
            log_it("info",f"Audit done, see {file_path}")
 
        case "event":
            with open(file_path, "w+t", encoding="utf-8") as event_r:
                event_r.write(f"\nEvents report")
                for event in cible.events.values():
                    event_r.write("\n----------------\n")
                    event_r.write(f"\nEvent: {event.eventType}")
                    event_r.write(f"\nEvent id type: {event.eventIdentifierType}")
                    event_r.write(f"\nEvent id: {event.eventIdentifierValue}")
                    event_r.write(f"\nEvent date time: {event.eventDateTime}")
                    event_r.write(f"\nEvent detail: {event.eventDetail}")
                    event_r.write(f"\nEvent outcome: {event.eventOutcome}")
                    event_r.write(f"\nEvent outcome detail note : {event.eventOutcomeDetailNote}")
                    # for items in event.linkingAgentIdentifier:
                    #     event_r.write(f"Cible agent identifier: [{items.agentIdentifierType}] {items.agentIdentifierValue}")
                    for items in event.linkingObjectIdentifier :
                        event_r.write(f"\nCible object identifier: [{items.linkingObjectIdentifierType}] {items.linkingObjectIdentifierValue} ")
            log_it("info",f"Events report done, see {file_path}")
        
        case "transfer":
            with open(file_path, "w+t", encoding="utf-8") as transf_r:
                transf_r.write("-----------")
                transf_r.write(f"\nTransfert report")

                for event in cible.events.values():
                    if event.eventType == "transfer":
                        transf_r.write(f"\nEvent id type: {event.eventIdentifierType}")
                        transf_r.write(f"\nEvent id: {event.eventIdentifierValue}")
                        transf_r.write(f"\nEvent date time: {event.eventDateTime}")
                        transf_r.write(f"\nEvent detail: {event.eventDetail}")
                        for items in event.linkingObjectIdentifier:
                            transf_r.write(f"\nCible object identifier: [{items.linkingObjectIdentifierType}] {items.linkingObjectIdentifierValue}")
            log_it("info",f"Transfer report done, see {file_path}")

        case "rename":
            with open(file_path, "w+t", encoding="utf-8") as rename_r:
                for event in cible.events.values():
                    if event.eventType == "filename change":
                        rename_r.write(f"\nEvent id type: {event.eventIdentifierType}")
                        rename_r.write(f"\nEvent detail: {event.eventDetail}")
                        for items in event.linkingObjectIdentifier:
                            transf_r.write(f"\nCible object identifier: [{items.linkingObjectIdentifierType}] {items.linkingObjectIdentifierValue}")

            log_it("info",f"Rename report done, see {file_path}")
        

        # case "uncompliant_zip":
        #     with open(file, "w+t", encoding="utf-8") as uncompliant_r:
        #         for packs in uncompliants_packages:
        #             uncompliant_r.write(f"\nEvent id type: {event.eventIdentifierType}")

def read_json_report(file_name:str, path: str) -> dict:
    file_path = os.path.join(path, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()   
    content = deserialize(content) 
    return content

def write_json_report(file_name: str, path: str, content:dict):
    file_path = os.path.join(path, file_name)
    # content = serialize(content)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f,  indent=4, ensure_ascii=False, sort_keys=True, default=str)