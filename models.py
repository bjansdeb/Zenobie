import uuid
from dataclasses import dataclass, field
from itertools import count


@dataclass
class Agent:
        agentName : str #Mets name #Premis agentName
        agentIdentifierType : str | None = "UUID"
        agentIdentifierValue : int= field(default_factory=lambda:uuid.uuid1()) #Premis #obligatoire partout #uuid1 calcule la valeur sur base du temps et de la machine
        agentType : str | None = "personne" #METS type #Premis agentType personne, organisation, logiciel
        note : str | None = None #Premis agentNote, facultatif, pour note additionnelle/complémentaire


"""
Basé sur Event dans PREMIS
The Event entity aggregates metadata about actions
Event est une action
"""    
@dataclass
class Event:
    eventIdentifierType : str | None = "UUID" #premis, obligatoire (local, UUID, )
    eventIdentifierValue : int = field(default_factory=lambda:uuid.uuid1()) #premis, obligatoire
    eventType : str | None = None#premis, obligatoire ; voir vc https://id.loc.gov/vocabulary/preservation/eventType.html
    eventDateTime : str |None = None #premis, obligatoire
    eventOutcomeDetailNote: str | None = ""
    linkingObjectIdentifierType : str | None = None #à dev plus tard
    linkingObjectIdentifierValue: str | None = None #à dév plus tard

    def set_agent(self, linkingAgentIdentifierType, linkingAgentIdentifierValue, linkingAgentRole):
        self.linkingAgentIdentifierType = linkingAgentIdentifierType
        self.linkingAgentIdentifierValue = linkingAgentIdentifierValue
        self.linkingAgentRole = linkingAgentRole

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
        objectIdentifierType : str | None = "UUID"
        objectIdentifierValue : int = field(default_factory=lambda:uuid.uuid1())
        formatName : str | None = None #premis obligatoire partout
        formatVersion : str | None = None #premis version du format mention en nom #facultatif
        formatRegistryName : str | None = None #premis Une désignation identifiant le registre de format référencé (Pronom) #obligatoire
        messageDigestAlgorithm : str | None = None #Premis, algo (md5..., etc) utilisé pour calculer le hash #obligatoire
        messageDigest : str | None = None  #Premis, output du calcul algo #obligatoire
        size : str | None = None #premis
        contentLocationType : str | None = None 
        contentLocationValue : str | None = None #valeur de URI
        originalName : str | None = None 
        events = []

        # def __eq__(self, copy_messageDigest):
        #     return self.messageDigest == copy_messageDigest

        def set_event(self, event):
            self.events.append(event)
    

class Report:
    def __init__(self, title, creation_time, author):
        self.title = title
        self.time = creation_time
        self.author = author
        self.actions = {}
       
    def record_it(self, action):
        self.actions.append(action)

@dataclass
class Right:
    rightsStatementIdentifierType: str | None = "UUID" #premis
    rightsStatementIdentifierValue: int = field(default_factory=lambda:uuid.uuid1()) #premis

@dataclass
class Mets:
    #hdr_ : métadonnées à l'intérieur du header <metsHdr>, qui comprend les métadonnées sur le document mets lui-même
    hdr_id : str | None = "H1"
    hdr_create_date : str | None = None
    hdr_last_mod : str | None = None
    hdr_id_producter : str |None = None
    hdr_id_production : str |None = None
    objects, events = [], []

    def set_agent(self, agent):
        self.agents= list[agent]
    
    def set_event(self, event):
        self.events.append(event)
    
    def set_right(self, right):
        self.right = list[right]
    
    def set_object(self, object):
        self.objects.append(object)

    # def get_object(self, object):
    #      self.objects.