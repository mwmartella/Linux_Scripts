#!/usr/bin/env bash
set -e

APP_DIR="/home/super1/Documents/Linux_Scripts"
cd "$APP_DIR"

# Activate the local venv so all dependencies are available
source "$APP_DIR/venv/bin/activate"

python3 -u MWSS_Field_Manager.py

