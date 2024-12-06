#!/bin/bash

REPO_URL="https://github.com/vitalygi/essh.git"
DEST_DIR="$HOME/.essh"
VENV_DIR=".venv"
PYTHON_VERSION="3.9.6"

add_to_path_immediate() {
    local path_entry="$1"
    local shell_rc

    if [[ "$SHELL" == */zsh ]]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.bashrc"
    fi

    if ! grep -Fxq "export PATH=\$PATH:$path_entry" "$shell_rc"; then
        echo "export PATH=\$PATH:$path_entry" >>"$shell_rc"
        echo "Path $path_entry added to $shell_rc."
    else
        echo "Path $path_entry is already present in $shell_rc."
    fi

    export PATH="$PATH:$path_entry"
    echo "Path $path_entry added to the current session."
}

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "Python not found. Attempting to install..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &>/dev/null; then
            sudo apt update
            sudo apt install -y python3 python3-venv python3-pip
        elif command -v yum &>/dev/null; then
            sudo yum install -y python3 python3-venv python3-pip
        else
            echo "Unknown package manager. Please install Python manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            brew install python
        else
            echo "Homebrew is not installed. Please install it manually (https://brew.sh)."
            exit 1
        fi
    else
        echo "Unsupported operating system. Please install Python manually."
        exit 1
    fi
fi

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "Python is not installed. Please install it manually."
    exit 1
fi

if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

if git clone --depth=1 "$REPO_URL" "$DEST_DIR"; then
    rm -rf $DEST_DIR/.git
    echo "Repository successfully cloned into $DEST_DIR."
else
    echo "Failed to clone the repository."
    exit 1
fi

cd "$DEST_DIR" || {
    echo "Failed to navigate to directory $DEST_DIR."
    exit 1
}

if $PYTHON_CMD -m venv "$VENV_DIR"; then
    echo "Virtual environment successfully created."
else
    echo "Failed to create virtual environment."
    exit 1
fi

ACTIVATE_SCRIPT="$DEST_DIR/$VENV_DIR/bin/activate"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT="$DEST_DIR/$VENV_DIR/Scripts/activate"
fi

if source "$ACTIVATE_SCRIPT"; then
    echo "Virtual environment activated."
else
    echo "Failed to activate virtual environment."
    exit 1
fi

if pip install -r requirements.txt; then
    echo "Dependencies installed successfully."
else
    echo "Failed to install dependencies."
    deactivate
    exit 1
fi

deactivate

echo "Adding bin to PATH..."
add_to_path_immediate "$DEST_DIR/bin"

echo "Installation complete."
cd ~