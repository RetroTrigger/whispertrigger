#!/bin/bash
# Script to build WhisperTrigger as an AppImage

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building WhisperTrigger AppImage..."

# Clean up any existing build artifacts
if [ -d "$SCRIPT_DIR/WhisperTrigger.AppDir" ]; then
    echo "Removing existing AppDir..."
    rm -rf "$SCRIPT_DIR/WhisperTrigger.AppDir"
fi

if [ -f "$SCRIPT_DIR/WhisperTrigger-x86_64.AppImage" ]; then
    echo "Removing existing AppImage..."
    rm -f "$SCRIPT_DIR/WhisperTrigger-x86_64.AppImage"
fi

if [ -f "$SCRIPT_DIR/appimagetool-x86_64.AppImage" ]; then
    echo "Removing existing AppImageTool..."
    rm -f "$SCRIPT_DIR/appimagetool-x86_64.AppImage"
fi

# Create AppDir structure
APPDIR="$SCRIPT_DIR/WhisperTrigger.AppDir"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/metainfo"

# Create a simple wrapper script
cat > "$APPDIR/usr/bin/whispertrigger" << 'EOF'
#!/bin/bash
# Get the directory where the AppImage is located
APPDIR="$(dirname "$(dirname "$(dirname "$0")")")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APPDIR/usr/lib/python3.10/site-packages:$PYTHONPATH"

# Run the application
python3 "$APPDIR/usr/lib/whispertrigger/main.py" "$@"
EOF
chmod +x "$APPDIR/usr/bin/whispertrigger"

# Copy application files
mkdir -p "$APPDIR/usr/lib/whispertrigger"
cp -r "$SCRIPT_DIR/src/"* "$APPDIR/usr/lib/whispertrigger/"

# Create .desktop file
cat > "$APPDIR/whispertrigger.desktop" << EOF
[Desktop Entry]
Name=WhisperTrigger
Comment=Speech-to-text application using OpenAI's Whisper
Exec=whispertrigger
Icon=whispertrigger
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=speech;voice;transcription;whisper;
EOF

# Also create it in the standard location
mkdir -p "$APPDIR/usr/share/applications"
cp "$APPDIR/whispertrigger.desktop" "$APPDIR/usr/share/applications/whispertrigger.desktop"

# Generate custom icon if it doesn't exist
if [ ! -f "$SCRIPT_DIR/resources/icon.png" ]; then
    echo "Creating custom icon..."
    # Check if we have pillow installed
    if ! python3 -c "import PIL" &> /dev/null; then
        echo "Installing Pillow for icon generation..."
        pip install pillow
    fi
    
    # Generate the icon using our custom script
    python3 "$SCRIPT_DIR/create_icon.py"
fi

# Generate icons if they don't exist
if [ ! -d "$SCRIPT_DIR/resources" ]; then
    mkdir -p "$SCRIPT_DIR/resources"
fi

# Generate icons using the Python script
echo "Generating icons..."
python3 "$SCRIPT_DIR/create_icon.py"

# Copy icons to AppDir
echo "Copying icons to AppDir..."

# Copy icon to root of AppDir (required by AppImageTool)
cp "$SCRIPT_DIR/resources/icon.png" "$APPDIR/whispertrigger.png"

# Also copy to application directory for direct access
mkdir -p "$APPDIR/usr/lib/whispertrigger/resources"
cp "$SCRIPT_DIR/resources/icon.png" "$APPDIR/usr/lib/whispertrigger/resources/icon.png"

# Copy to standard locations for desktop integration
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cp "$SCRIPT_DIR/resources/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/whispertrigger.png"

# Also copy smaller icons
for size in 128 64 32; do
    if [ -f "$SCRIPT_DIR/resources/icon_${size}.png" ]; then
        # Copy to application resources
        cp "$SCRIPT_DIR/resources/icon_${size}.png" "$APPDIR/usr/lib/whispertrigger/resources/icon_${size}.png"
        
        # Copy to system icon directories
        mkdir -p "$APPDIR/usr/share/icons/hicolor/${size}x${size}/apps"
        cp "$SCRIPT_DIR/resources/icon_${size}.png" "$APPDIR/usr/share/icons/hicolor/${size}x${size}/apps/whispertrigger.png"
    fi
done

# Create a symlink for .DirIcon (used by some desktop environments)
ln -sf "whispertrigger.png" "$APPDIR/.DirIcon"

# Create AppStream metadata
mkdir -p "$APPDIR/usr/share/metainfo"
cat > "$APPDIR/usr/share/metainfo/io.github.whispertrigger.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>io.github.whispertrigger</id>
  <name>WhisperTrigger</name>
  <summary>Speech-to-text application using OpenAI's Whisper</summary>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <description>
    <p>
      WhisperTrigger is an open-source speech-to-text application for Linux that uses
      OpenAI's Whisper model to transcribe speech with high accuracy.
    </p>
    <p>
      Features include real-time transcription, multiple processing modes, global
      keyboard shortcuts, and visual feedback with waveform visualization.
    </p>
  </description>
  <categories>
    <category>AudioVideo</category>
    <category>Audio</category>
    <category>Utility</category>
  </categories>
  <url type="homepage">https://github.com/RetroTrigger/whispertrigger</url>
  <provides>
    <binary>whispertrigger</binary>
  </provides>
  <releases>
    <release version="1.0.0" date="$(date +%Y-%m-%d)">
      <description>
        <p>Initial release</p>
      </description>
    </release>
  </releases>
  <content_rating type="oars-1.1" />
</component>
EOF

# Create AppRun script
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
# Get the directory where the AppImage is located
APPDIR="$(dirname "$0")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APPDIR/usr/lib/python3.10/site-packages:$PYTHONPATH"

# Run the application
python3 "$APPDIR/usr/lib/whispertrigger/main.py" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Check for NVIDIA GPU
check_nvidia_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        if nvidia-smi -L &> /dev/null; then
            return 0  # NVIDIA GPU found
        fi
    fi
    return 1  # No NVIDIA GPU found
}

# Create virtual environment and install dependencies
echo "Creating Python virtual environment and installing dependencies..."
python3 -m venv "$APPDIR/usr/lib/venv"
source "$APPDIR/usr/lib/venv/bin/activate"
pip install --upgrade pip

# Choose requirements file based on GPU presence
if check_nvidia_gpu; then
    echo "NVIDIA GPU detected, installing with CUDA support..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "No NVIDIA GPU detected, installing CPU-only version..."
    pip install -r "$SCRIPT_DIR/requirements-cpu.txt"
fi

# Copy Python packages to AppDir
mkdir -p "$APPDIR/usr/lib/python3.10/site-packages"
cp -r "$APPDIR/usr/lib/venv/lib/python3.10/site-packages/"* "$APPDIR/usr/lib/python3.10/site-packages/"

# Download AppImageTool if not present
if [ ! -f "$SCRIPT_DIR/appimagetool-x86_64.AppImage" ]; then
    echo "Downloading AppImageTool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$SCRIPT_DIR/appimagetool-x86_64.AppImage"
    chmod +x "$SCRIPT_DIR/appimagetool-x86_64.AppImage"
fi

# Build the AppImage
echo "Building the AppImage..."
# Use --no-appstream flag to ignore AppStream validation warnings
ARCH=x86_64 "$SCRIPT_DIR/appimagetool-x86_64.AppImage" --no-appstream "$APPDIR" "$SCRIPT_DIR/WhisperTrigger-x86_64.AppImage"

# Check if the AppImage was created successfully
if [ -f "$SCRIPT_DIR/WhisperTrigger-x86_64.AppImage" ]; then
    echo "AppImage created: $SCRIPT_DIR/WhisperTrigger-x86_64.AppImage"
    echo "You can now distribute this file to other Linux users."
    
    # Clean up temporary files
    echo "Cleaning up temporary files..."
    rm -rf "$APPDIR"
    rm -f "$SCRIPT_DIR/appimagetool-x86_64.AppImage"
    
    # Create a .gitignore entry for AppImage if it doesn't exist
    if [ ! -f "$SCRIPT_DIR/.gitignore" ]; then
        echo "Creating .gitignore file..."
        echo "# Ignore AppImage build artifacts" > "$SCRIPT_DIR/.gitignore"
        echo "*.AppImage" >> "$SCRIPT_DIR/.gitignore"
        echo "WhisperTrigger.AppDir/" >> "$SCRIPT_DIR/.gitignore"
    elif ! grep -q "*.AppImage" "$SCRIPT_DIR/.gitignore"; then
        echo "Adding AppImage entries to .gitignore..."
        echo "\n# Ignore AppImage build artifacts" >> "$SCRIPT_DIR/.gitignore"
        echo "*.AppImage" >> "$SCRIPT_DIR/.gitignore"
        echo "WhisperTrigger.AppDir/" >> "$SCRIPT_DIR/.gitignore"
    fi
    
    echo "Cleanup complete."
else
    echo "Error: AppImage creation failed."
    exit 1
fi
