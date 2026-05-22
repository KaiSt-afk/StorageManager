# Storage Manager

Storage Manager is a cross-platform Python desktop/mobile app built with BeeWare and Toga. It helps manage storage areas and the content inside them from a single interface.

## Features

- Create storage areas.
- Prevent duplicate area names.
- View areas in a table.
- Delete areas.
- Select an area to view its content.
- Open dialogs and windows for adding or editing entries.
- Save and load project data from files.

## Tech Stack

- Python
- BeeWare
- Toga
- Briefcase

BeeWare is a toolkit for building native apps in Python across platforms such as iOS, Android, Windows, macOS, Linux, web, and tvOS [web:3]. Toga is BeeWare’s native GUI toolkit [web:179]. Briefcase is used to build and package the app [web:181].

## Project Structure

```text
project/
├── entity.py
├── main.py
└── README.md
```

## Requirements

- Python 3.x
- BeeWare / Toga
- Briefcase
- pysmb

## Installation

Clone the repository:

```bash
git clone https://github.com/KaiSt-afk/StorageManager.git
cd StorageManager
```


Create and activate a virtual environment:

add .fish in second line if fish shell is used

```bash
python -m venv .venv
source .venv/bin/activate
```



## Running the app

If you are using Briefcase:

```bash
briefcase dev
```

For mobile or platform builds:

```bash
briefcase run android
briefcase run ios
```

## Usage

1. Start the app.
2. Add a new storage area using the **Add Area** button.
3. Enter a unique name for the area.
4. Select areas to manage their content.
5. Delete or edit entries as needed.

## Notes

- Area names must be unique.
- Input errors are shown directly in the UI.
- The app is designed to work with mobile touch input as well as desktop input.

## Development

To add new features, work mainly in the Toga UI layer and your Python model classes. BeeWare apps are written in Python and use native-looking interfaces on each platform [web:3][web:179].

## Author

Kai St
