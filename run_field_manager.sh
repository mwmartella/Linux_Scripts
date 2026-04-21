#!/usr/bin/env bash
set -e

# Resolve the directory this script lives in, regardless of where it's called from
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

# Activate the local venv so all dependencies are available
source "$APP_DIR/venv/bin/activate"

python3 -u MWSS_Field_Manager.py
