# Field Manager - Desktop Launcher Setup

## Install Python dependencies (run once)

### Create a virtual environment and install packages:
```bash
cd ~/Documents/Linux_Scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

If `python3 -m venv` fails, install the venv package first:
```bash
sudo apt install python3-venv
```

---

## After pulling files to the tablet, run these commands:

### 1. Make the launcher script executable
```bash
chmod +x ~/Documents/Linux_Scripts/run_field_manager.sh
```

### 2. Copy desktop icons to desktop
```bash
cp ~/Documents/Linux_Scripts/FieldManager.desktop ~/Desktop/
cp ~/Documents/Linux_Scripts/FieldManager-Debug.desktop ~/Desktop/
```

### 3. Make them executable
```bash
chmod +x ~/Desktop/FieldManager.desktop
chmod +x ~/Desktop/FieldManager-Debug.desktop
```

### 4. (Optional) Add to application menu
```bash
mkdir -p ~/.local/share/applications
cp ~/Desktop/FieldManager.desktop ~/.local/share/applications/
```

### 5. Right-click each icon on the desktop → "Allow Launching"

---

## Notes
- **Field Manager** — runs the app with no terminal window. Logs saved to `~/Documents/Linux_Scripts/field_manager.log`
- **Field Manager (Debug)** — opens a terminal so you can see print output live
- To view logs: `tail -f ~/Documents/Linux_Scripts/field_manager.log`

