import csv
import os
from dataclasses import dataclass, field

@dataclass
class Agent:
        agentName : str #Mets name #Premis agentName
        agentIdentifierType : str | None = "local"
        agentType : str | None = "personne" #METS type #Premis agentType personne, organisation, logiciel
        note : str | None = None #Premis agentNote, facultatif, pour note additionnelle/complémentaire

        _agentIdentifierValue = 0 #Premis #obligatoire partout

        def __post_init__(self):
            self._agentIdentifierValue +=1    

"""
Basé sur Event dans PREMIS
The Event entity aggregates metadata about actions
Event est une action
"""    
class Event:
    def __init__(self,eventIdentifierType, eventIdentifierValue, eventType, eventDateTime):
        self.eventIdentifierType = eventIdentifierType #premis, obligatoire (local, UUID, )
        self.eventIdentifierValue = eventIdentifierValue #premis, obligatoire
        self.eventType = eventType #premis, obligatoire ; voir vc https://id.loc.gov/vocabulary/preservation/eventType.html
        self.eventDateTime = eventDateTime #premis, obligatoire
    
    def set_agent(self, agent):
        self.agent = agent
    
    def display_metadata(self):
        print(self.eventIdentifierType, self.eventIdentifierValue, 
              self.eventType, self.eventDateTime, self.agent)


"""
Object basé sur Object dans Premis

"""

@dataclass
class State:
    title : str
    author : str
    role : str | None = None
    full_size : str | None = None
    date : str | None = None
    depth : str | None = None
    stats : str | None = None

@dataclass
class Object:
        objectIdentifierType : str | None = "local"
        # objectIdentifierValue : int = field(init=False) #premis obligatoire partout 
        formatName : str | None = None #premis obligatoire partout
        formatVersion : str | None = None #premis version du format mention en nom #facultatif
        formatRegistryName : str | None = None #premis Une désignation identifiant le registre de format référencé (Pronom) #obligatoire
        messageDigestAlgorithm : str | None = None #Premis, algo (md5..., etc) utilisé pour calculer le hash #obligatoire
        messageDigest : str | None = None  #Premis, output du calcul algo #obligatoire
        size : str | None = None #premis
        contentLocationType : str | None = None 
        contentLocationValue : str | None = None #valeur de URI 

        _objectIdentifierValue = 0 #premis obligatoire partout 

        def __post_init__(self):
            self._objectIdentifierValue +=1
            print("id caché:", self._objectIdentifierValue)                

class Report:
    def __init__(self, title, creation_time, author):
        self.title = title
        self.time = creation_time
        self.author = author
        self.actions = {}
       
    def record_it(self, action):
        self.actions.append(action)

class Right:
    def __init__(self,rightsStatementIdentifierType, rightsStatementIdentifierValue):
        self.rightsStatementIdentifierType = rightsStatementIdentifierType #premis
        self.rightsStatementIdentifierValue = rightsStatementIdentifierValue  #premis

class Mets:
    def __init__(self, hdr_id, hdr_create_date, 
                 hdr_last_mod, hdr_id_producter, hdr_id_production):
        
        self.hdr_id = hdr_id
        self.hdr_create_date = hdr_create_date
        self.hdr_last_mod = hdr_last_mod
        self.hdr_id_producter = hdr_id_producter
        self.hdr_id_production = hdr_id_production
        self.objects = []
    
    def set_agent(self, agent):
        self.agents= list[agent]
    
    def set_event(self, event):
        self.event= list[event]
    
    def set_right(self, right):
        self.right = list[right]
    
    def set_object(self, object):
        self.objects.append(object)

    def write_report(self, file_name, path, type, cible= None):
        file = os.path.join(path, file_name)
        if type =="hash":
            with open(file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_name', 'hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for object in self.objects :
                    writer.writerow({'object_name': {object.contentLocationValue}, 'hash': {object.messageDigest}})
            print(f"Hash report done, see {file}")
        elif type=="state":            
            with open(file, "w+t") as state_r:
                state_r.write(f"Audit of {cible.title}")
                state_r.write(f"\nSize of the repository" + cible.full_size + " bytes")
                state_r.write(f"\nMax-depth: {cible.depth}")
                state_r.write(f"\nStats : {cible.stats}")
                state_r.write(f"\nReport done with Zenobie at {cible.date} by {cible.author} ({cible.role})")
            print(f"Audit done, see {file}")