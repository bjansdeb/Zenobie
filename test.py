import uuid
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Data:
    uid : int = field(default_factory= lambda:uuid.uuid1().hex)
    url : str | None = None

    def update_path(self, new_url):
        self.url = new_url

@dataclass
class CentralRegistre:
    collection : dict[str, Data] = field(default_factory=dict)
    #tri par path/uri
    uris : list[str, Data] = field(default_factory=dict)

    def add_data(self, data):
        self.collection[data.uid] = data.url

    def add_uri(self, data):
        self.uris[data.url] = data.uid

    def update_collection(self, data):
        self.collection[data.uid] = data.url
    
    def update_uri(self, data):
        old_path = data.url
        data.update_path("citron")
        self.uris[data.url] = self.uris.pop(old_path)





registre = CentralRegistre()
data = Data(url="cerf")
registre.add_data(data)
registre.add_uri(data)

print("before update: ", "collection:", registre.collection, "registre.uris :", registre.uris, data.url)
registre.update_uri(data)
registre.update_collection(data)
print("after update: ", "collection:", registre.collection, "registre.uris :", registre.uris, data.url)