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

# Check for NVIDIA GPU
check_nvidia_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        if nvidia-smi -L &> /dev/null; then
            return 0  # NVIDIA GPU found
        fi
    fi
    return 1  # No NVIDIA GPU found
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    
    # Choose requirements file based on GPU presence
    if check_nvidia_gpu; then
        echo "NVIDIA GPU detected, installing with CUDA support..."
        pip install -r requirements.txt
    else
        echo "No NVIDIA GPU detected, installing CPU-only version..."
        pip install -r requirements-cpu.txt
    fi
else
    source venv/bin/activate
fi

# Create resources directory if it doesn't exist
mkdir -p resources

# Check if icon exists
if [ ! -f "resources/icon.png" ]; then
    echo "Creating custom icon..."
    # Check if we have pillow installed
    if ! python3 -c "import PIL" &> /dev/null; then
        echo "Installing Pillow for icon generation..."
        pip install pillow
    fi
    
    # Generate the icon using our custom script
    python3 create_icon.py
fi

# Run the application
echo "Starting WhisperTrigger..."
python3 src/main.py "$@"
