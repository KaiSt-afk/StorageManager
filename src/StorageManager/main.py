import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import entity

#TODO everything needs to be in one window only content changes and Dialaog boxes are fine
class StorageApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title="Storage Manager")
        self.main_area_box = toga.Box(style=Pack(direction=COLUMN, gap= 5))
        self.error_label = toga.Label("", style=Pack(color="red"))

        #buttons in the main Window
        add_button = toga.Button("Add Area", on_press=self.addAreaGUI)
        overview_button = toga.Button("Overview", on_press=self.overviewContent)
        load_button = toga.Button("Load", on_press=lambda widget: self.loadAndRefresh())
        save_button = toga.Button("Save", on_press=lambda widget: entity.save())

        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(add_button)
        button_row.add(overview_button)
        button_row.add(load_button)
        button_row.add(save_button)

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

        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        self.main_box.add(button_row)
        self.main_box.add(self.main_area_box)
        self.main_box.add(self.error_label)
        self.commands.add(saveto, loadfrom)

        self.main_window.content = self.main_box
        self.main_window.show()

    #pick other location and change name if wanted
    async def saveDifferentLocation(self, widget):
        path = await self.main_window.save_file_dialog(title="Save as",
                                                       suggested_filename="savedLayout.json")
        entity.save(path)

    #pick other file to load from apparently not working on mobil
    async def loadDifferentLocation(self, widget):
        path = await self.main_window.open_file_dialog(title="Choose a file")
        entity.load(path)
        self.refresh_areas()

    #load from savedLayout and refreshes the gui
    def loadAndRefresh(self):
        entity.load()
        self.refresh_areas()

    #TODO remove as own Window maybe as Dialog window???
    #add a new Area to store Content in
    def addAreaGUI(self, widget):
        self.add_window = toga.Window(title="Create Area", size=(320, 180))

        self.name_input = toga.TextInput(
            placeholder="Enter area name",
            style=Pack(flex=1)
        )
        self.error_label = toga.Label("", style=Pack(color="red"))

        def create_area(widget):
            name = self.name_input.value.strip()
            if not name or any(area.name == name for area in entity.allAreas):
                self.error_label.text = "Name already exists."
            else:
                entity.Area.create(name)
                self.refresh_areas()
                self.add_window.close()


        create_button = toga.Button("Create", on_press=create_area)
        cancel_button = toga.Button("Cancel", on_press=lambda w: self.add_window.close())

        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(create_button)
        button_row.add(cancel_button)

        box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        box.add(toga.Label("Area name:"))
        box.add(self.name_input)
        box.add(self.error_label)
        box.add(button_row)

        self.add_window.content = box
        self.add_window.show()



    #renders the displayed areas again
    def refresh_areas(self):
        self.main_area_box.clear()
        self.error_label.text = ""
        print(entity.allAreas)
        if not entity.allAreas:
            self.main_area_box.add(toga.Label("No areas yet."))
            return

        for i, area in enumerate(entity.allAreas):
            row = toga.Box(style=Pack(direction=ROW, gap=10, margin=5))

            label = toga.Label(area.name, style=Pack(flex=1))
            delete_button = toga.Button("Delete", on_press=lambda w, idx=i: self.delete_area(idx))

            checkoutButton = toga.Button("Checkout", on_press=lambda w, idx=i: self.checkoutArea(idx))

            row.add(label)
            row.add(checkoutButton)
            row.add(delete_button)
            self.main_area_box.add(row)

    #removes area and refreshes the gui
    def delete_area(self, index):
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
            self.main_window.content = self.main_box
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

        self.main_window.content = box

    #renders the displayed content again
    def refresh_content(self):
        i = self.current_Area_Index
        self.checkout_content_box.clear()
        self.error_label.text = ""
        print(entity.allAreas[i].content)
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
        self.refresh_content()

    #amount to add to given content at index, default is 1
    def addAmount(self, content, idx, amountadd = 1):
        content[idx].amount = content[idx].amount + amountadd
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
        self.main_window.content = box

    def changeToMainWindow(self, widget):
        self.main_window.content = self.main_box

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



def main():
    return StorageApp("Storage Manager", "com.example.storagemanager")

if __name__ == "__main__":
    main().main_loop()