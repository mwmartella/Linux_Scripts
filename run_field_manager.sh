#!/usr/bin/env bash

# Resolve the directory this script lives in, regardless of where it's called from
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

LOG="$APP_DIR/field_manager.log"
echo "=== $(date) ===" >> "$LOG"
echo "APP_DIR: $APP_DIR" >> "$LOG"

# Ensure tkinter is installed (it's a system package, not pip-installable)
if ! python3 -c "import tkinter" &>/dev/null; then
    echo "tkinter not found — installing python3-tk..." >> "$LOG"
    sudo apt-get install -y python3-tk >> "$LOG" 2>&1
fi

# Activate the local venv if it exists, otherwise fall back to system python3
if [ -f "$APP_DIR/venv/bin/activate" ]; then
    source "$APP_DIR/venv/bin/activate"
    echo "venv activated" >> "$LOG"
else
    echo "WARNING: venv not found at $APP_DIR/venv — using system python3" >> "$LOG"
    echo "To create it run:  python3 -m venv $APP_DIR/venv && $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt"
fi

python3 -u MWSS_Field_Manager.py >> "$LOG" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: MWSS_Field_Manager.py exited with code $EXIT_CODE" >> "$LOG"
    # Show a visible error popup so it doesn't silently disappear
    which zenity &>/dev/null && zenity --error --text="Field Manager crashed (exit $EXIT_CODE).\nSee log:\n$LOG" --title="Field Manager Error"
fi
