#!/bin/bash
# WhisperTrigger launch script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required system dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    # Check for pip
    if ! command_exists pip3; then
        missing_deps+=("python3-pip")
    fi
    
    # Check for FFmpeg
    if ! command_exists ffmpeg; then
        missing_deps+=("ffmpeg")
    fi
    
    # Check for xdotool
    if ! command_exists xdotool; then
        missing_deps+=("xdotool")
    fi
    
    # Check for Qt dependencies
    if ! dpkg -l | grep -q libxcb-cursor0; then
        missing_deps+=("libxcb-cursor0")
    fi
    
    # Check for Python venv
    if ! python3 -m venv --help >/dev/null 2>&1; then
        missing_deps+=("python3-venv")
    fi
    
    # Check for PortAudio
    if ! dpkg -l | grep -q portaudio19-dev; then
        missing_deps+=("portaudio19-dev")
    fi
    
    # If there are missing dependencies, try to install them
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "The following dependencies are missing: ${missing_deps[*]}"
        
        # Check if we can use sudo
        if command_exists sudo; then
            echo "Attempting to install missing dependencies..."
            if sudo apt-get update && sudo apt-get install -y "${missing_deps[@]}"; then
                echo "Dependencies installed successfully."
            else
                echo "Failed to install dependencies. Please install them manually:"
                echo "sudo apt-get install ${missing_deps[*]}"
                exit 1
            fi
        else
            echo "Please install the missing dependencies manually:"
            echo "sudo apt-get install ${missing_deps[*]}"
            exit 1
        fi
    fi
}

# Run dependency check
check_dependencies

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Create resources directory if it doesn't exist
mkdir -p resources

# Check if icon exists
if [ ! -f "resources/icon.png" ]; then
    echo "Creating default icon..."
    # Create a simple icon using imagemagick if available
    if command -v convert &> /dev/null; then
        convert -size 128x128 radial-gradient:blue-purple resources/icon.png
    fi
fi

# Run the application
echo "Starting WhisperTrigger..."
python3 src/main.py "$@"
