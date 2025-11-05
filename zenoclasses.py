class User:
    def __init__(self, name, role, institution):
        self.name = name
        self.role = role
        self.institution = institution
    
class Action:
    def __init__(self, id, description, user, time):
        self.id = id
        self.description = description
        self.user = user
        self.time = time
