import asyncio
from dataclasses import asdict
from datetime import date, datetime
import json
from functools import partial
from smb.SMBConnection import SMBConnection

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from StorageManager import entity

class StorageApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title="Storage Manager")
        self.main_area_box = toga.Box(style=Pack(direction=COLUMN, gap= 5))
        self.error_label = toga.Label("", style=Pack(color="red"))
        self.importLabel = toga.Label("")

        #buttons in the main Window
        add_button = toga.Button("Add Area", on_press=self.addAreaGUI)
        overview_button = toga.Button("Overview", on_press=self.overviewContent)
        load_button = toga.Button("Load", on_press=self.load)
        save_button = toga.Button("Save", on_press=self.save)
        export_button = toga.Button("Export", on_press=self.exportNAS)
        import_button = toga.Button("Import", on_press=self.importNAS)
        remoteConfig_button = toga.Button("Set Config", on_press=self.remoteConfig)

        #one row for save/load buttons
        saveload_row = toga.Box(style=Pack(direction=ROW, gap=10))
        saveload_row.add(load_button)
        saveload_row.add(save_button)
        saveload_row.add(export_button)
        saveload_row.add(import_button)
        saveload_row.add(remoteConfig_button)
        #one row for app buttons
        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(add_button)
        button_row.add(overview_button)

        saveLoad = toga.Group("save/Load")
        saveto = toga.Command(
            self.saveDifferentLocation,
            text="Save to..",
            tooltip="Save to..",
            group=saveLoad,
        )
        loadfrom = toga.Command(
            self.loadDifferentLocation,
            text="Load from..",
            tooltip="Load from..",
            group=saveLoad,
        )

        #params for export to set and use in in/export if remoteConfig exists load it else default values
        self.local_path = self.paths.data / "savedLayout.json"
        self.configPath = self.paths.data / "remoteConfig.json"
        if self.configPath.is_file():
            with open(self.configPath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.server_ip = data["server_ip"]
            self.server_name = data["server_name"]
            self.share_name = data["share_name"]
            self.port = data["port"]
            self.remote_path = data["remote_path"]
            self.username = data["username"]
            self.password = data["password"]
        else:
            self.server_ip = "192.168.178.1"
            self.server_name = "FRITZ!Box 7490"
            self.share_name = "FRITZ.NAS"
            self.port= 445
            self.remote_path = "StorageManager/savedLayout.json"
            self.username = "StorageManager"
            self.password = ""

        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        self.main_box.add(saveload_row)
        self.main_box.add(button_row)
        self.main_box.add(self.importLabel)
        self.main_box.add(self.main_area_box)
        self.main_box.add(self.error_label)
        self.commands.add(saveto, loadfrom)

        self.mainscroll = toga.ScrollContainer(content=self.main_box)

        self.main_window.on_close = self.on_close
        self.main_window.content = self.mainscroll
        self.main_window.show()

        asyncio.create_task(self.importNAS(None))



    #pick other location and change name if wanted
    async def saveDifferentLocation(self, widget):
        path = await self.main_window.save_file_dialog(title="Save as",
                                                       suggested_filename="savedLayout.json")
        entity.save(path)

    #pick other file to load from not working on mobil !!!!!!!!!!!!!!!!!
    async def loadDifferentLocation(self, widget):
        path = await self.main_window.open_file_dialog(title="Choose a file")
        entity.load(path)
        self.refresh_areas()

    #saves to savedLayout
    def save(self, widget):
        path = self.paths.data / "savedLayout.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        def converter(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        data = [asdict(area) for area in entity.allAreas]
        data.append({"Importdate" : self.importLabel.text})

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, default=converter, indent=4)
        #print("saved")

    #load from savedLayout and refreshes the gui
    def load(self, widget):
        entity.allAreas.clear()
        path = self.paths.data / "savedLayout.json"

        with open(path, "r") as f:
            data = json.load(f)

        for area_data in data[:-1]: #last item is importdate
            contents = [
                entity.Content(
                    name=c["name"],
                    amount=c["amount"],
                    unit=c["unit"],
                    date=date.fromisoformat(c["date"])
                )
                for c in area_data["content"]
            ]

            area = entity.Area(
                name=area_data["name"],
                content=contents
            )

            entity.allAreas.append(area)
        importDate = data[-1].get("Importdate", "")
        self.importLabel.text = importDate
        self.refresh_areas()
        #print("loaded")

    #export to NAS params set in local_path, server_ip, server_name, remote_path, username, password
    async def exportNAS(self, widget):
        self.save(widget)
        #export the currently local saved file to NAS
        conn = SMBConnection(
            self.username,
            self.password,
            "StorageManagerClient",
            self.server_name,
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        try:
            conn.connect(self.server_ip, self.port)
            with open(self.local_path, "rb") as f:
                conn.storeFile(self.share_name, self.remote_path, f)
            conn.close()
        except:
            await self.main_window.dialog(toga.InfoDialog("Connection failed", "check Parameter"))


    #import from NAS params set in local_path, server_ip, server_name, remote_path, username, password
    async def importNAS(self, widget):
        #import from NAS to the currently local file
        conn = SMBConnection(
            self.username,
            self.password,
            "StorageManagerClient",
            self.server_name,
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        try:
            conn.connect(self.server_ip, self.port, timeout=15)
            with open(self.local_path, "wb") as f:
                conn.retrieveFile(self.share_name, self.remote_path, f)
            conn.close()
            self.load(widget)
            self.importLabel.text = datetime.now().strftime("%d-%m-%y %H:%M")
        except Exception as e:
            print(e)
            await self.main_window.dialog(toga.InfoDialog("Connection failed", "check Parameter"))

    #lets user set all Config Params
    def remoteConfig(self, widget):
        #sets the current config and saves it
        def saveConfig(widget):
            sip = self.serverIPInput.value.strip()
            sn = self.serverNameInput.value.strip()
            shn = self.shareNameInput.value.strip()
            po = self.portInput.value
            rp = self.remotePathInput.value.strip()
            un = self.usernameInput.value.strip()
            pw = self.passwordInput.value.strip()
            if sip:
                self.server_ip = sip
            if sn:
                self.server_name = sn
            if shn:
                self.share_name = shn
            if po:
                self.port = int(po)
            if rp:
                self.remote_path = rp
            if un:
                self.username = un
            if pw:
                self.password = pw
            path = self.paths.data / "remoteConfig.json"
            data = {
                "server_ip": self.server_ip,
                "server_name": self.server_name,
                "share_name": self.share_name,
                "port": int(self.port),
                "remote_path": self.remote_path,
                "username": self.username,
                "password": self.password,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        #removes Config file but keeps Config while app is running
        def rmConfig(widget):
            if self.configPath.is_file():
                self.configPath.unlink()
        #create Input Field for each Param
        serverIPLabel = toga.Label("Server IP:")
        self.serverIPInput = toga.TextInput(placeholder=self.server_ip)
        serverNameLabel = toga.Label("Server Name:")
        self.serverNameInput = toga.TextInput(placeholder=self.server_name)
        shareNameLabel = toga.Label("Share Name:")
        self.shareNameInput = toga.TextInput(placeholder=self.share_name)
        portLabel = toga.Label("Port:")
        self.portInput = toga.NumberInput(value=self.port)
        remotePathLabel = toga.Label("remote Path: ")
        self.remotePathInput = toga.TextInput(placeholder=self.remote_path)
        usernameLabel = toga.Label("Username:")
        self.usernameInput = toga.TextInput(placeholder=self.username)
        passwordLabel = toga.Label("Password:")
        self.passwordInput = toga.TextInput(placeholder="Enter Password")
        goBack = toga.Button("Go Back", on_press=self.changeToMainWindow)
        setConfig = toga.Button("Set Config", on_press=saveConfig)
        removeConfig = toga.Button("remove Config", on_press=rmConfig)

        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(setConfig)
        button_row.add(goBack)
        button_row.add(removeConfig)

        box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        box.add(serverIPLabel)
        box.add(self.serverIPInput)
        box.add(serverNameLabel)
        box.add(self.serverNameInput)
        box.add(shareNameLabel)
        box.add(self.shareNameInput)
        box.add(portLabel)
        box.add(self.portInput)
        box.add(remotePathLabel)
        box.add(self.remotePathInput)
        box.add(usernameLabel)
        box.add(self.usernameInput)
        box.add(passwordLabel)
        box.add(self.passwordInput)
        box.add(self.error_label)
        box.add(button_row)

        boxscroll = toga.ScrollContainer(content=box)
        self.main_window.content = boxscroll

    #add a new Area to store Content in
    def addAreaGUI(self, widget):
        self.name_input = toga.TextInput(
            placeholder="Enter area name",
            style=Pack(flex=1)
        )
        self.error_label = toga.Label("", style=Pack(color="red"))

        #add area when name entered and valid
        def create_area(widget):
            name = self.name_input.value.strip()
            if not name or any(area.name == name for area in entity.allAreas):
                self.error_label.text = "Name already exists."
            else:
                entity.Area.create(name)
                self.refresh_areas()
                self.main_window.content = self.mainscroll

        create_button = toga.Button("Create", on_press=create_area)
        cancel_button = toga.Button("Cancel", on_press=self.goBack)

        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(create_button)
        button_row.add(cancel_button)

        box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        box.add(toga.Label("Area name:"))
        box.add(self.name_input)
        box.add(self.error_label)
        box.add(button_row)

        boxscroll = toga.ScrollContainer(content=box)
        self.main_window.content = boxscroll

    #reopen main window
    def goBack(self, widget):
        self.main_window.content = self.mainscroll
        self.refresh_areas()


    #renders the displayed areas again
    def refresh_areas(self):
        self.main_area_box.clear()
        self.error_label.text = ""
        #print(entity.allAreas)
        if not entity.allAreas:
            self.main_area_box.add(toga.Label("No areas yet."))
            return

        for i, area in enumerate(entity.allAreas):
            row = toga.Box(style=Pack(direction=ROW, gap=10, margin=5))

            label = toga.Label(area.name, style=Pack(flex=1))
            delete_button = toga.Button("Delete", on_press=partial(self.delete_area, index= i))
            checkoutButton = toga.Button("Checkout", on_press=lambda w, idx=i: self.checkoutArea(idx))

            row.add(label)
            row.add(checkoutButton)
            row.add(delete_button)
            self.main_area_box.add(row)

    #removes area and refreshes the gui
    async def delete_area(self, widget, index):
        confirm = await self.main_window.dialog(toga.QuestionDialog("Delete area", "Do you really want to delete this area?"))
        if confirm:
            entity.allAreas.pop(index)
            self.refresh_areas()

    #END main Window



    #Window inside of areas get index of which area from entity.allAreas
    def checkoutArea(self, i):
        cArea = entity.allAreas[i]
        self.current_Area_Index = i
        self.checkout_content_box = toga.Box(style=Pack(direction=COLUMN, gap= 5))
        self.refresh_content()

        self.name_input = toga.TextInput(
            placeholder="Enter Content name",
            style=Pack(flex=1)
        )
        self.amount_input = toga.NumberInput(
            value= 0,
            style=Pack(flex=1)
        )
        self.unit_input = toga.TextInput(
            placeholder="Enter Unit",
            style=Pack(flex=1)
        )

        self.areaName_input = toga.TextInput(
            placeholder="Enter new Area name",
            style=Pack(flex=1)
        )
        areaNameButton = toga.Button("Confirm Change", on_press=self.changeAreaName)

        input_row = toga.Box(style=Pack(direction=ROW, gap=10))
        input_row.add(self.name_input, self.amount_input, self.unit_input)

        def add_Content(widget):
            name = self.name_input.value.strip()
            amount = int(self.amount_input.value)
            unit = self.unit_input.value.strip()
            if name and unit:
                entity.allAreas[self.current_Area_Index].content.append(entity.Content(name, amount, unit))
                entity.allAreas[self.current_Area_Index].content.sort(key= lambda c: c.name)
                self.name_input.value = ""
                self.amount_input.value = 0
                self.unit_input.value = ""
                self.refresh_content()

        #closes checkout Window and refreshes Area to update if a name changed
        def goBack(widget):
            self.main_window.content = self.mainscroll
            self.refresh_areas()

        addContent_button = toga.Button("Add Content", on_press=add_Content)
        back_button = toga.Button("Go Back", on_press= goBack)

        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(addContent_button)
        button_row.add(back_button)

        self.checkout_name_label = toga.Label(f"Add Content to {entity.allAreas[i].name}:")

        box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        box.add(self.checkout_name_label)
        box.add(input_row)
        box.add(button_row)
        box.add(self.checkout_content_box)
        box.add(self.error_label)
        box.add(toga.Box(style=Pack(flex=1)))
        box.add(toga.Label("Change Areaname: "))
        box.add(self.areaName_input)
        box.add(areaNameButton)

        boxscroll = toga.ScrollContainer(content=box)
        self.main_window.content = boxscroll

    #renders the displayed content again
    def refresh_content(self):
        i = self.current_Area_Index
        self.checkout_content_box.clear()
        self.error_label.text = ""
        #print(entity.allAreas[i].content)
        if not entity.allAreas[i].content:
            self.checkout_content_box.add(toga.Label("No content yet."))
            return

        for j, content in enumerate(entity.allAreas[i].content):
            row = toga.Box(style=Pack(direction=ROW, gap=10, margin=5))
            datestr = content.date.strftime("%m - %y")
            labelstr = f"{content.name}   {content.amount} {content.unit}    Date: {datestr}"
            label = toga.Label(labelstr, style=Pack(flex=1))
            removeAllButton = toga.Button("remove All", on_press=lambda w, idx=j: self.delete_content(
                entity.allAreas[i].content, idx))

            remove1Button = toga.Button("remove 1", on_press=lambda w, idx=j: self.rmAmount(entity.allAreas[i].content, idx))

            add1Button = toga.Button("add 1", on_press=lambda w, idx=j: self.addAmount(entity.allAreas[i].content, idx))

            row.add(label)
            row.add(add1Button)
            row.add(remove1Button)
            row.add(removeAllButton)
            self.checkout_content_box.add(row)


    #removes content and refreshes the gui argument is the content and index to remove
    def delete_content(self, content, idx):
        content.pop(idx)
        self.refresh_content()

    #amount to remove from given content at index, default is 1
    def rmAmount(self, content, idx, amountremove = 1):
        content[idx].amount = content[idx].amount - amountremove
        content[idx].date = date.today()
        self.refresh_content()

    #amount to add to given content at index, default is 1
    def addAmount(self, content, idx, amountadd = 1):
        content[idx].amount = content[idx].amount + amountadd
        content[idx].date = date.today()
        self.refresh_content()

    #changing name and check if name already exists
    def changeAreaName(self, widget):
        name = self.areaName_input.value.strip()

        if any(area for area in entity.allAreas if area.name == name):
            self.error_label.text = "Name already exists."
        else:
            entity.allAreas[self.current_Area_Index].changeName(name)
            self.checkout_name_label.text= f"Add Content to {name}:"
            self.areaName_input.value = ""
            self.error_label.text = ""

    #END Window checkout Area


    #create a overview for content in all Areas (not adding them up)
    def overviewContent(self, widget):
        tableData = []
        #add all data as tuples in a list
        for area in entity.allAreas:
            for content in area.content:
                datestr = content.date.strftime("%m - %y")
                tableData.append((area.name, content.name, content.amount, content.unit, datestr))
        tableData.sort(key=lambda content: content[1])

        #create the table
        contentTable = toga.Table(columns=["area", "content", "amount", "unit", "date"], data=tableData, style=Pack(flex=1),
                                  on_select=self.openAreaCheckout)
        box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        back_button = toga.Button("Go Back", on_press=self.changeToMainWindow)

        box.add(back_button)
        box.add(contentTable)
        boxscroll = toga.ScrollContainer(content=box)
        self.main_window.content = boxscroll

    def changeToMainWindow(self, widget):
        self.error_label.text = ""
        self.main_window.content = self.mainscroll

    #when click on a row in table then open the area of this row and close overview window
    def openAreaCheckout(self, widget):
        areaName = widget.selection.area
        if areaName is None:
            return
        area = next((area for area in entity.allAreas if areaName == area.name), None)
        if area is None:
            return

        idx = next(i for i, a in enumerate(entity.allAreas) if a.name == area.name)
        self.checkoutArea(idx)

    #END overview Window


    #when closed auto save and export
    async def on_close(self, widget):
        print("TEST")
        self.save(widget)
        await self.exportNAS(widget)
        return True



def main():
    return StorageApp("Storage Manager", "com.example.storagemanager")

if __name__ == "__main__":
    main().main_loop()