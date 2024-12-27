# KSP Anchor Keeper

A Python utility that fixes the "floating anchor" bug in Kerbal Space Program (KSP) where Stamp-O-Tron Ground Anchors gradually drift upwards when reloading saves.

## ⚠️ Important Notice

Please note that this script is still **under development**. 

I cannot guarantee error-free functionality. Therefore, it is **strongly recommended** to create backups of your save files before using the script.

⚠️ **Use at your own risk!**

## Problem
In KSP, Stamp-O-Tron Ground Anchors have a known issue where their altitude increases slightly every time a save is loaded. Over time, this causes anchored vessels to drift away from the ground.

## Solution
This tool:
1. Monitors your KSP save directory for changes
2. Stores the original position of each ground anchor in a SQLite database when first deployed
3. Automatically restores anchors to their original positions whenever the save file is modified

## Requirements
- Python 3.12+
- KSP with Stamp-O-Tron Ground Anchors
- Required Python packages:
  - sfsutils >= 1.1.1
  - watchdog >= 6.0.0

## Installation
```bash
# Clone the repository
git clone https://github.com/OliverWieland/ksp-anchor-keeper

# Install dependencies
pip install -r requirements.txt
```

## Usage
1. Edit 

main.py

 to set 

directory_to_watch

 to your KSP saves folder
2. Run the script:
```bash
python main.py
```
3. The tool will run in the background and automatically fix anchor positions whenever you save your game

## Configuration

You can configure the tool in two ways:

1. Create a `config.yaml` file:
```yaml
saves_directory: "~/KSP/saves"
database_path: "anchors.db"
```

## How it Works
- Uses 

watchdog

 to monitor KSP save files (.sfs) for changes
- Parses save files using 

sfsutils

 to extract ground anchor data
- Stores original anchor positions in 

anchors.db


- Restores original position data when altitude/height changes are detected
- Handles multiple anchors and persists data between sessions

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
