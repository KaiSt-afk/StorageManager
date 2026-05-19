from dataclasses import dataclass, field, asdict
from datetime import date
import json


@dataclass
class Content:
    name: str
    amount: int
    unit: str
    date: date = date.today()#Format: YYY-MM-DD #date.strftime("%m-%y") to get other format but then string type

@dataclass
class Area:
    name: str
    content : list[Content] = field(default_factory=list)

    def create(name: str):
        if not any(area.name == name for area in allAreas):
            area = Area(name)
            allAreas.append(area)
            return area

    def addContent(self, con: Content):
        self.content.append(con)

    def rmContent(self, con: Content):
        #maybe add try catch to safe if content doesnt exist
            self.content.remove(con)

    def changeName(self, name: str):
        if any(area for area in allAreas if area.name == name):
            return
        self.name = name



#every Area created gets added to this
allAreas: list[Area] = []



#saves to savedLayout if no other path given
def save(path:str = "savedLayout.json"):
    global allAreas

    def converter(obj):
        if isinstance(obj, date):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


    with open(path, "w") as f:
        json.dump(
            [asdict(area) for area in allAreas],
            f,
            default=converter,
            indent=4
        )
    print("saved")

#load from given path if none then tries from savedLayout
def load(path:str = "savedLayout.json"):
    global allAreas
    allAreas.clear()

    with open(path, "r") as f:
        data = json.load(f)

    for area_data in data:
        contents = [
            Content(
                name=c["name"],
                amount=c["amount"],
                unit=c["unit"],
                date=date.fromisoformat(c["date"])
            )
            for c in area_data["content"]
        ]

        area = Area(
            name=area_data["name"],
            content=contents
        )

        allAreas.append(area)
    print("loaded")
