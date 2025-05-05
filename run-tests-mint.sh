#!/bin/bash

# Usage: ./run_tests-mint.sh /path/to/config/folder

CONFIG_FOLDER="$1"

if [ -z "$CONFIG_FOLDER" ]; then
  echo "Usage: $0 /path/to/config/folder"
  exit 1
fi

for cfg_file in "$CONFIG_FOLDER"/*.cfg; do
  full_path=$(realpath "$cfg_file")

  echo "Opening new terminal window for $cfg_file"

  gnome-terminal -- bash -c "cd \"$(pwd)\"; python3 router.py \"$full_path\"; exec bash"
done
