#!/bin/bash
# Sync from Windows (Cursor) to WSL. Run: bash /mnt/c/W26/project/NeuroEGE/sync-from-win.sh
SRC="/mnt/c/W26/project/NeuroEGE"
DST="$HOME/NeuroEGE"
rsync -av --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' --exclude '.env' --exclude 'db.sqlite3' --exclude 'staticfiles' "$SRC/" "$DST/"
echo "Synced at $(date)"

