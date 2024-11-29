#!/bin/bash


REPO_URL="https://github.com/vitalygi/essh.git"
DEST_DIR="$HOME/.essh"


if git clone "$REPO_URL" "$DEST_DIR"; then
    echo "Repository cloned successfully into $DEST_DIR."
else
    echo "Failed to clone the repository."
    exit 1
fi

cd "$DEST_DIR" || {
    echo "Failed to navigate to $DEST_DIR";
    exit 1;
}

if python3 -m venv .venv; then
    echo "Virtual environment created successfully."
else
    echo "Failed to create virtual environment."
    exit 1
fi

source $DEST_DIR/.venv/bin/activate
chmod +x essh
if pip install -r requirements.txt; then
    echo "Dependencies installed successfully."
else
    echo "Failed to install dependencies."
    deactivate
    exit 1
fi
