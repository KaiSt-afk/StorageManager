import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import entity


class StorageApp(toga.App):
    def startup(self):

        self.main_window = toga.MainWindow(title="Storage Manager")
        self.area_box = toga.Box(style=Pack(direction=COLUMN, gap= 5))

        #buttons in the main Window
        add_button = toga.Button("Add Area", on_press=self.addAreaGUI)
        load_button = toga.Button("Load", on_press=lambda widget: self.loadAndRefresh())
        save_button = toga.Button("Save", on_press=lambda widget: entity.save())

        button_row = toga.Box(style=Pack(direction=ROW, gap=10))
        button_row.add(add_button)
        button_row.add(load_button)
        button_row.add(save_button)

        main_box = toga.Box(style=Pack(direction=COLUMN, margin=10, gap=10))
        main_box.add(button_row)
        main_box.add(self.area_box)

        self.main_window.content = main_box
        self.main_window.show()

    #load from savedLayout and refreshes the gui
    def loadAndRefresh(self):
        entity.load()
        self.refresh_areas()

    #add a new Area to store Content in
    def addAreaGUI(self, widget):
        self.add_window = toga.Window(title="Create Area", size=(320, 180))

        self.name_input = toga.TextInput(
            placeholder="Enter area name",
            style=Pack(flex=1)
        )

        def create_area(widget):
            name = self.name_input.value.strip()
            if name:
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
        box.add(button_row)

        self.add_window.content = box
        self.add_window.show()



    #renders the displayed areas again
    def refresh_areas(self):
        self.area_box.clear()
        print(entity.allAreas)
        if not entity.allAreas:
            self.area_box.add(toga.Label("No areas yet."))
            return

        for idx, area in enumerate(entity.allAreas):
            row = toga.Box(style=Pack(direction=ROW, gap=10, margin=5))

            label = toga.Label(area.name, style=Pack(flex=1))
            delete_button = toga.Button("Delete", on_press=lambda w, i=idx: self.delete_area(i))

            checkoutButton = toga.Button("Checkout", on_press=lambda w, i=idx: print("TODO"))

            row.add(label)
            row.add(checkoutButton)
            row.add(delete_button)
            self.area_box.add(row)

    #removes area and refreshes the gui
    def delete_area(self, index):
        entity.allAreas.pop(index)
        self.refresh_areas()


def main():
    return StorageApp("Storage Manager", "com.example.storagemanager")

if __name__ == "__main__":
    main().main_loop()