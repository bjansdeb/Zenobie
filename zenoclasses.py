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
        print(self.eventIdentifierType, self.eventIdentifierValue, self.eventType, self.eventDateTime, self.agent)


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

    # def create_hash_csv(self, title, report_rep):
    #     csvfile = open(title, 'w', newline='', encoding='utf-8') #à corriger
    #     hash_report = csv.writer(csvfile)
    #     for root, dir, files in os.walk(source): 
    #         for file in files :
    #             f =os.path.join(root, file)
    #             md5 = hash_calculator(f)
    #             hash_report.writerow([f])
    #             hash_report.writerow([md5])            

    def record_it(self, action):
        ...

class Right:
    def __init__(self,rightsStatementIdentifierType, rightsStatementIdentifierValue):
        self.rightsStatementIdentifierType = rightsStatementIdentifierType #premis
        self.rightsStatementIdentifierValue = rightsStatementIdentifierValue  #premis
