import csv

class Agent:
    def __init__(self, id, name, role, agent_type, institution, note):
        self.id = id #Premis
        self.name = name #Mets name #Premis agentName
        self.role = role #Mets role
        self.agent_type = agent_type #METS type #Premis agentType personne, organisation, logiciel
        self.institution = institution
        self.note = note #Premis agentNote, facultatif, pour note additionnelle/complémentaire

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

class Object:
    def __init__(self, objectIdentifierValue, formatName, formatVersion, formatRegistryName,
                 messageDigestAlgorithm, messageDigest, size):
        self.objectIdentifierValue = objectIdentifierValue #premis obligatoire, 
        self.formatName = formatName #premis obligatoire
        self.formatVersion = formatVersion #premis version du format mention en nom #facultatif
        self.formatRegistryName = formatRegistryName #premis Une désignation identifiant le registre de format référencé (Pronom) #obligatoire
        self.messageDigestAlgorithm = messageDigestAlgorithm #Premis, algo (md5..., etc) utilisé pour calculer le hash #obligatoire
        self.messageDigest = messageDigest  #Premis, output du calcul algo #obligatoire
        self.size = size #premis

class Report:
    def __init__(self, title, creation_time, author):
        self.title = title
        self.time = creation_time
        self.author = author
        self.actions = {}
       
    def record_it(self, action):
        ...

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
    def set_agent(self, agent):
        self.agents= list[agent]
    def set_event(self, event):
        self.event= list[event]
    def set_right(self, right):
        self.right = list[right]
    def set_object(self, object):
        self.object = list[object]
    def write_report(self, file_name, object, type):
        if type =="hash":
            with open(file_name, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_name', 'hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'object_name': {object.name}, 'hash': {object.hash}})