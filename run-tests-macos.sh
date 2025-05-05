#!/bin/bash

# Usage: ./run_tests.sh /path/to/config/folder

CONFIG_FOLDER="$1"

if [ -z "$CONFIG_FOLDER" ]; then
  echo "Usage: $0 /path/to/config/folder"
  exit 1
fi

for cfg_file in "$CONFIG_FOLDER"/*.conf; do
  full_path=$(realpath "$cfg_file")
  
  echo "Opening new terminal window for $cfg_file"

  osascript <<EOF
tell application "Terminal"
    activate
    do script "cd \"$(pwd)\"; python3 router.py \"$full_path\""
end tell
EOF

done
