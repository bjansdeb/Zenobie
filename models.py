import uuid
from dataclasses import dataclass, field
from itertools import count
from vocabularies import *

#PREMIS metadata originated from https://www.loc.gov/standards/premis/v3/premis-hierarchical-3-0.html

@dataclass
class Agent:
    """3.1    agentIdentifier (M, R)"""
    agentIdentifierType : str | None = "UUID"
    agentIdentifierValue : str= field(default_factory=lambda:uuid.uuid1().hex) #Premis #obligatoire partout #uuid1 calcule la valeur sur base du temps et de la machine
    """3.2    agentName (O, R)"""
    agentName : str | None = None #Mets name #Premis agentName
    """3.3    agentType (O, NR)"""
    agentType : str | None = "personne" #METS type #Premis agentType [personne, organisation, logiciel]
    """3.4    agentVersion (O, NR)"""
    agentVersion : str | None = None
    """3.5    agentNote (O, R)"""
    note : str | None = None #Premis agentNote, facultatif, pour note additionnelle/complémentaire
    """3.6    agentExtension (O, R)"""
    agentExtension : str | None = None #Premis container pour les éléments hors PREMIS

    """3.7 linkingEventIdentifier (O, R)""" #container
    linkingEventIdentifierType : str | None = None  #(M, NR)
    linkingEventIdentifierValue : str | None = None # (M, NR)
    """3.8 linkingRightsStatementIdentifier (O, R)"""#container
    linkingRightsStatementIdentifierType : str | None = None # (M, NR)
    linkingRightsStatementIdentifierValue : str | None = None # (M, NR)
    """3.9 linkingEnvironmentIdentifier (O, R)""" #container
    linkingEnvironmentIdentifierType : str | None = None # (M, NR)
    linkingEnvironmentIdentifierValue : str | None = None # (M, NR)
    linkingEnvironmentRole : str | None = None # (O, R)


"""
Basé sur Event dans PREMIS
The Event entity aggregates metadata about actions
Event est une action
"""    
@dataclass
class Event:
    """2.1    eventIdentifier (M, NR)"""
    eventIdentifierType : str | None = "UUID" #premis, obligatoire (local, UUID, )
    eventIdentifierValue : str = field(default_factory=lambda:uuid.uuid1().hex) #premis, obligatoire
    """2.2    eventType (M, NR)"""
    eventType : EventType | None = None  #premis, obligatoire

    """2.3    eventDateTime (M, NR)"""
    eventDateTime : str |None = None #premis, obligatoire
    """2.4    eventDetailInformation (O, R)"""
    eventDetail : str | None = None
    eventDetailExtension : str | None = None
    """2.5    eventOutcomeInformation (O, R)"""
    eventOutcome : str = "Success" 
    eventOutcomeDetailNote: str | None = ""

    """2.6    linkingAgentIdentifier (O, R)"""
    linkingAgentIdentifierType : str =""
    linkingAgentIdentifierValue : str = ""
    linkingAgentRole : str = "" 

    """2.7    linkingObjectIdentifier (O, R)"""
    linkingObjectIdentifierType : str | None = None #à dev plus tard
    linkingObjectIdentifierValue: str | None = None #à dév plus tard
    linkingObjectRole : str | None = None #à dév plus tard



    def set_agent(self, linkingAgentIdentifierType, linkingAgentIdentifierValue, linkingAgentRole):
        self.linkingAgentIdentifierType = linkingAgentIdentifierType
        self.linkingAgentIdentifierValue = linkingAgentIdentifierValue
        self.linkingAgentRole = linkingAgentRole

    def display_metadata(self):
        print(self.eventIdentifierType, self.eventIdentifierValue, 
              self.eventType, self.eventDateTime, self.agent)



@dataclass
class State:
    title : str
    author : str
    role : str | None = None
    full_size : str | None = None
    date : str | None = None
    depth : str | None = None
    stats : str | None = None

"""
Object basé sur Object dans Premis
"""
@dataclass
class Object:
    """1.1 objectIdentifier"""
    objectIdentifierType : str | None = "UUID" #(M, NR)
    objectIdentifierValue : str = field(default_factory=lambda:uuid.uuid1().hex) #(M, NR)
    formatRegistryName : str | None = None #premis Une désignation identifiant le registre de format référencé (Pronom) #obligatoire
    
    """1.2    objectCategory (M, NR)"""
    objectCategory : str | None = None
    """1.3 preservationLevel [Intellectual Entity/Representation/File]"""
    
    """1.4    significantProperties (O, R)"""
    significantProperties: str | None = None #(propriété significative) (O, R)
    significantPropertiesType: str | None = None #(type de propriété significative) (O, NR)
    significantPropertiesValue: str | None = None #(valeur de la propriété significative) (O, NR)
    significantPropertiesExtension: str | None = None #(extension pour les propriétés significatives) (O, # R) 

    """1.5    objectCharacteristics [File/Bitstream]""" #(M, R, File / Bitstream not IE/R)

    """1.6    originalName (O, NR) [Intellectual Entity, Representation, File]"""

    """1.7    storage (O, R) [Representation, File, Bitstream]"""

    """1.8    signatureInformation (O, R) [File, Bitstream]"""

    ##Non implémenté à ce stade, propre à PREMIS 3
    """1.9    environmentFunction (O, R) [Intellectual Entity of type environment]"""
    """1.10  environmentDesignation (O, R) [Intellectual Entity of type environment]"""
    """1.11  environmentRegistry (O, R) [Intellectual Entity of type environment]"""
    """1.12  environmentExtension (O, R) [Intellectual Entity of type environment]"""
    ##Non implémenté à ce stade, propre à PREMIS 3


    relations = []
    """1.13 relationship (O, R)"""
    """relations documentation"""
    """Information about a relationship between this Object and one or more
    other Objects."""
    """Dans le cas de event, permet de documenter """
    relationshipType : RelationshipType | None = None #(M, NR) exemple : "derivation"
    relationshipSubType : RelationshipSubType |None = None #(M, NR) exemple : "has source"
    """1.13.3 relatedObjectIdentifier (M, R)"""
    relatedObjectIdentifierType : str | None = None #(M, R) #exemple : "REPPID"
    relatedObjectIdentifierValue : str | None = None #(M, R) #exemple : "17415495"
    relatedObjectSequence: str | None = None #(O, NR)

    """1.13.4 relatedEventIdentifier (O, R) """
    """An Object may be related to another Object because of an Event, for example, migration."""
    relatedEventIdentifierType : str | None = None #(M, NR)
    relatedEventIdentifierValue : str | None = None #(M, NR)
    relatedEventSequence : str | None = None #(O, NR) 

    events = []
    """linking documentation"""
    """Used to link to Events that are not associated with relationships
    between Objects, such as format validation, virus checking, etc. """
    """1.14  linkingEventIdentifier (O, R)""" #container
    #The eventIdentifier of an Event associated with the Object.
    #The eventIdentifierValue value of the related Event (Must be an existing eventIdentifierValue value.).
    linkingEventIdentifierType :str | None = None #(M, NR)
    linkingEventIdentifierValue : str | None = None #(M, NR)
    """1.15  linkingRightsStatementIdentifier #(O, R)""" #container 
    linkingRightsStatementIdentifierType : str | None = None # (M, NR)
    linkingRightsStatementIdentifierValue : str | None = None #(M, NR)        


    # def __eq__(self, copy_messageDigest):
    #     return self.messageDigest == copy_messageDigest
    def set_linking_event(self, event):
        self.events.append(event)



#enfants de Object, pour les trois types conseillés par PREMIS
@dataclass
class Bitstream(Object):
    """1.5    objectCharacteristics [file/bitstream]""" #(M, R, File / Bitstream not IE/R)
    compositionLevel : str | None = None #(O, NR) [File, Bitstream]
    """1.5.2 fixity""" #(O, R) [File, Bitstream]
    messageDigestAlgorithm : str | None = None #(M, NR)Premis, algo (md5..., etc) utilisé pour calculer le hash #obligatoire
    messageDigest : str | None = None  #(M, NR) [File, Bitstream] Premis, output du calcul algo #obligatoire     
    messageDigestOriginator : str | None = None #(O, NR) [File, Bitstream]
    
    """1.5.3 size"""
    size : int | None = None #(O, NR) [File, Bitstream] premis

    """1.5.4 format""" #(M, R) [File, Bitstream]
    """1.5.4.1 formatDesignation""" # (O, NR) [File, Bitstream]
    formatName : str | None = None #(M, NR)
    formatVersion : str | None = None #(O, NR)
    """1.5.4.2 formatRegistry"""  #(O, NR)
    formatRegistryName : str | None = None # (M, NR) exemple : "PRONOM"
    formatRegistryKey : str | None = None  #(M, NR)
    formatRegistryRole : str | None = None #(O, NR) exemple : "specification"

    """1.5.5    creatingApplication (O, R) [File, Bitstream]"""
    creatingApplicationName : str | None = None #(O, NR) [File, Bitstream]
    creatingApplicationVersion : str | None = None #(O, NR) [File, Bitstream]
    dateCreatedByApplication : str | None = None #(O, NR) [File, Bitstream]
    creatingApplicationExtension : str | None = None #(O, R) [File, Bitstream]
    """1.5.6    inhibitors (O, R) [File, Bitstream]"""
    inhibitorType  : str | None = None  #(M, NR) [File, Bitstream]
    inhibitorTarget  : str | None = None #(O, R) [File, Bitstream]
    inhibitorKey : str | None = None  #(O, NR) [File, Bitstream]
    """1.5.7    objectCharacteristicsExtension"""
    objectCharacteristicsExtension : str | None = None     #(O, R) [File, Bitstream]

    """1.7    storage (O, R) [Representation, File, Bitstream]"""
    """1.7.1    contentLocation (O, NR) [Representation, File, Bitstream]""" #container
    contentLocationType : str | None = None  #(M, NR) [Representation, File, Bitstream]
    contentLocationValue : str | None = None #(M, NR) [Representation, File, Bitstream]

    """1.7.2    storageMedium (O, NR) [Representation, File, Bitstream]"""

    """1.8    signatureInformation (O, R) [File, Bitstream]"""
    """1.8.1    signature (O, R) [File, Bitstream]""" #container
    signatureEncoding : str | None = None #(M, NR) [File, Bitstream]
    signer : str | None = None  #(O, NR) [File, Bitstream]
    signatureMethod : str | None = None  # (M, NR) [File, Bitstream]
    signatureValue : str | None = None # (M, NR) [File, Bitstream]
    signatureValidationRules : str | None = None # (M, NR) [File, Bitstream]
    signatureProperties : str | None = None # (O, R) [File, Bitstream]
    keyInformation : str | None = None #(O, NR) [File, Bitstream]
    """1.8.2    signatureInformationExtension (O, R) [File, Bitstream]"""
    signatureInformationExtension : str | None = None   

@dataclass
class File(Object):
    """1.3 preservationLevel [representation/file/intellectual entity]"""
    preservationLevelType : str | None = None 
    preservationLevelValue : str | None = None #(M, NR)
    preservationLevelRole : str | None = None #(O, NR)
    preservationLevelRationale : str | None = None #(O, R) 
    preservationLevelDateAssigned : str | None = None #(O, NR) 

    """1.5    objectCharacteristics [file/bitstream]""" #(M, R, File / Bitstream not IE/R)
    compositionLevel : str | None = None #(O, NR) [File, Bitstream]
    """1.5.2 fixity""" #(O, R) [File, Bitstream]
    messageDigestAlgorithm : str | None = None #(M, NR)Premis, algo (md5..., etc) utilisé pour calculer le hash #obligatoire
    messageDigest : str | None = None  #(M, NR) [File, Bitstream] Premis, output du calcul algo #obligatoire     
    messageDigestOriginator : str | None = None #(O, NR) [File, Bitstream]
    
    """1.5.3 size"""
    size : int | None = None #(O, NR) [File, Bitstream] premis

    """1.5.4 format""" #(M, R) [File, Bitstream]
    """1.5.4.1 formatDesignation""" # (O, NR) [File, Bitstream]
    formatName : str | None = None #(M, NR)
    formatVersion : str | None = None #(O, NR)
    """1.5.4.2 formatRegistry"""  #(O, NR)
    formatRegistryName : str | None = None # (M, NR) exemple : "PRONOM"
    formatRegistryKey : str | None = None  #(M, NR)
    formatRegistryRole : str | None = None #(O, NR) exemple : "specification"

    """1.5.5    creatingApplication (O, R) [File, Bitstream]"""
    creatingApplicationName : str | None = None #(O, NR) [File, Bitstream]
    creatingApplicationVersion : str | None = None #(O, NR) [File, Bitstream]
    dateCreatedByApplication : str | None = None #(O, NR) [File, Bitstream]
    creatingApplicationExtension : str | None = None #(O, R) [File, Bitstream]
    """1.5.6    inhibitors (O, R) [File, Bitstream]"""
    inhibitorType  : str | None = None  #(M, NR) [File, Bitstream]
    inhibitorTarget  : str | None = None #(O, R) [File, Bitstream]
    inhibitorKey : str | None = None  #(O, NR) [File, Bitstream]
    """1.5.7    objectCharacteristicsExtension"""
    objectCharacteristicsExtension : str | None = None     #(O, R) [File, Bitstream]
    
    """1.6    originalName (O, NR) [Intellectual Entity, Representation, File]"""
    originalName : str | None = None 

    """1.7    storage (O, R) [Representation, File, Bitstream]"""
    """1.7.1    contentLocation (O, NR) [Representation, File, Bitstream]""" #container
    contentLocationType : str | None = None  #(M, NR) [Representation, File, Bitstream]
    contentLocationValue : str | None = None #(M, NR) [Representation, File, Bitstream]

    """1.7.2    storageMedium (O, NR) [Representation, File, Bitstream]"""

    """1.8    signatureInformation (O, R) [File, Bitstream]"""
    """1.8.1    signature (O, R) [File, Bitstream]""" #container
    signatureEncoding : str | None = None #(M, NR) [File, Bitstream]
    signer : str | None  = None #(O, NR) [File, Bitstream]
    signatureMethod : str | None  = None # (M, NR) [File, Bitstream]
    signatureValue : str | None = None# (M, NR) [File, Bitstream]
    signatureValidationRules : str | None = None # (M, NR) [File, Bitstream]
    signatureProperties : str | None = None # (O, R) [File, Bitstream]
    keyInformation : str | None  = None #(O, NR) [File, Bitstream]
    """1.8.2    signatureInformationExtension (O, R) [File, Bitstream]"""
    signatureInformationExtension : str | None = None   

@dataclass
class IntellectualEntity(Object):
    """1.3 preservationLevel [representation/file/intellectual entity]"""
    preservationLevelType : str | None = None 
    preservationLevelValue : str | None = None #(M, NR)
    preservationLevelRole : str | None = None #(O, NR)
    preservationLevelRationale : str | None = None #(O, R) 
    preservationLevelDateAssigned : str | None = None #(O, NR) 
   
    """1.6    originalName (O, NR) [Intellectual Entity, Representation, File]"""
    originalName : str | None = None 

@dataclass    
class Representation(Object):
    """1.3 preservationLevel [representation/file]"""
    preservationLevelType : str | None = None 
    preservationLevelValue : str | None = None #(M, NR)
    preservationLevelRole : str | None = None #(O, NR)
    preservationLevelRationale : str | None = None #(O, R) 
    preservationLevelDateAssigned : str | None = None #(O, NR) 
    
    """1.6    originalName (O, NR) [Intellectual Entity, Representation, File]"""
    originalName : str | None = None 

    """1.7    storage (O, R) [Representation, File, Bitstream]"""
    """1.7.1    contentLocation (O, NR) [Representation, File, Bitstream]""" #container
    contentLocationType : str | None = None  #(M, NR) [Representation, File, Bitstream]
    contentLocationValue : str | None = None #(M, NR) [Representation, File, Bitstream]

    """1.7.2    storageMedium (O, NR) [Representation, File, Bitstream]"""


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
    rightsStatementIdentifierValue: str = field(default_factory=lambda:uuid.uuid1().hex) #premis

@dataclass
class PremisObjects:
    """
    Docstring for PremisObjects
    Recense tous les objets PREMIS créés au cours du processus
    Contient un jeu de clés physiques provisoires pour suivre les objets via leurs URIS
    """
    #tri par UUID
    agents : dict[str, Agent] = field(default_factory=dict) 
    events : dict[str, Event] = field(default_factory=dict)
    objects : dict[str, Object] = field(default_factory=dict)
    rights : dict[str, Right] = field(default_factory=dict)
    
    #tri par path/uri
    uris : list[str, Object] = field(default_factory=dict)
    
    def add_agent(self, agent):
        self.agents[agent.agentIdentifierValue] = agent
    
    def add_event(self, event):
        self.events[event.eventIdentifierValue] = event
    
    def add_right(self, right):
        self.rights[right.rightsStatementIdentifierValue] = right
    
    def add_object(self, object):
        self.objects[object.objectIdentifierValue] = object
    
    def add_uri(self, uri, object):
        self.uris[uri] = object.objectIdentifierValue

    def adapt_uri(self, objects, new_uri): #à corriger
        for object in objects.values():
            self.uris[object.objectIdentifierValue] = new_uri

    def get_uris(self):
        print(self.uris)

@dataclass
class Mets:
    #hdr_ : métadonnées à l'intérieur du header <metsHdr>, qui comprend les métadonnées sur le document mets lui-même
    hdr_id : str | None = "H1"
    hdr_create_date : str | None = None
    hdr_last_mod : str | None = None
    hdr_id_producter : str |None = None
    hdr_id_production : str |None = None
