#!/bin/bash

# Define the source folder and file you want to install
SOURCE_FOLDER="resources"
SOURCE_FILE="main.py"
SOURCE_FILE1="easy_json.py"
DESKTOP_FILE="no-skip-video-player.desktop"

# Define the destination directory for the folder and file
DEST_DIR="/usr/bin/no-skip-video-player"

# Check if the script is run as root (required to copy files to /usr/bin)
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Create the destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy the folder to /usr/bin/
if [ -d "$SOURCE_FOLDER" ]; then
  cp -r "$SOURCE_FOLDER" "$DEST_DIR"
  echo "image folder added to $DEST_DIR"
else
  echo "Source folder $SOURCE_FOLDER does not exist"
  exit 1
fi

# Copy the file to /usr/bin/
if [ -f "$SOURCE_FILE" ]; then
  cp "$SOURCE_FILE" "$DEST_DIR"
  cp "$SOURCE_FILE1" "$DEST_DIR"
  echo "script added to $DEST_DIR"
else
  echo "Source file $SOURCE_FILE does not exist"
  exit 1
fi

# Add a newline and the alias to the current user's ~/.bashrc (not root's)
USER_HOME=$(eval echo ~${SUDO_USER})
APPLICATIONS_FOLDER="$USER_HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_FOLDER"

if [ -f "$USER_HOME/.bashrc" ]; then
  echo -e "\nalias enjoyporn='python3 /usr/bin/no-skip-video-player/main.py'" >> "$USER_HOME/.bashrc"
  echo "Alias 'enjoyporn' added to $USER_HOME/.bashrc"
  cp "$DESKTOP_FILE" "$APPLICATIONS_FOLDER"
  echo "no-skip-video-player.desktop added to .local/share/applications"
else
  echo "$USER_HOME/.bashrc not found, alias not added"
fi

# Notify the user that the installation is complete
echo "Installation complete. Please restart your terminal or run 'source ~/.bashrc' to use 'enjoyporn'."
