class Agent:
    def __init__(self, id, name, role, agent_type, institution, note):
        self.id = id #Premis
        self.name = name #Mets name #Premis agentName
        self.role = role #Mets role
        self.agent_type = agent_type #METS type #Premis agentType personne, organisation, logiciel
        self.institution = institution
        self.note = note #Premis agentNote, facultatif, pour note additionnelle/complémentaire

"""Basé sur Event dans PREMIS
The Event entity aggregates metadata about actions
"""    
class Action:
    def __init__(self, id, description, user, time):
        self.id = id
        self.description = description
        self.user = user
        self.time = time
class Report:
    def __init__(self, title, creation_time, author):
        self.title = title
        self.time = creation_time
        self.author = author
        self.actions = {}
    
    def record_it(self, action):
        ...
