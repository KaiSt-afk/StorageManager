from dataclasses import dataclass, field
from datetime import date


@dataclass
class Content:
    name: str
    amount: str
    date = date.today().strftime("%m-%y") #Format: MM-YY

@dataclass
class Area:
    name: str
    content : list[Content] = field(default_factory=list)

    def create(name: str):
        area = Area(name)
        allAreas.append(area)
        return area

    def addContent(self, con: Content):
        self.content.append(con)

    def rmContent(self, con: Content):
        #maybe add try catch to safe if content doesnt exist
            self.content.remove(con)

    def changeName(self, name: str):
        self.name = name


#every Area created gets added to this
allAreas: list[Area] = []


#TODO safe allAreas here as JSON ig
#saves to SavedLayout if no other path given
def save(path:str = "SavedLayout"):
    return

#load from given path if none then tries from SavedLayout
def load(path:str = "SavedLayout"):
    return

