#!/bin/bash
# Script to build WhisperTrigger as an AppImage

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building WhisperTrigger AppImage..."

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
cat > "$APPDIR/usr/share/applications/whispertrigger.desktop" << EOF
[Desktop Entry]
Name=WhisperTrigger
Comment=Speech-to-text application using OpenAI's Whisper
Exec=whispertrigger
Icon=whispertrigger
Terminal=false
Type=Application
Categories=Utility;Audio;
Keywords=speech;voice;transcription;whisper;
EOF

# Check for ImageMagick
if ! command -v convert &> /dev/null; then
    echo "ImageMagick not found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y imagemagick
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y ImageMagick
    elif command -v yum &> /dev/null; then
        sudo yum install -y ImageMagick
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm imagemagick
    else
        echo "Could not install ImageMagick automatically. Please install it manually."
        echo "On Ubuntu/Debian: sudo apt-get install imagemagick"
        echo "On Fedora: sudo dnf install ImageMagick"
        echo "On CentOS/RHEL: sudo yum install ImageMagick"
        echo "On Arch: sudo pacman -S imagemagick"
        exit 1
    fi
    
    # Check if installation was successful
    if ! command -v convert &> /dev/null; then
        echo "Failed to install ImageMagick. Please install it manually."
        exit 1
    fi
    echo "ImageMagick installed successfully."
fi

# Copy icon
if [ -f "$SCRIPT_DIR/resources/icon.png" ]; then
    cp "$SCRIPT_DIR/resources/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/whispertrigger.png"
else
    # Create a simple icon if it doesn't exist
    echo "Creating icon using ImageMagick..."
    convert -size 256x256 radial-gradient:blue-purple "$APPDIR/usr/share/icons/hicolor/256x256/apps/whispertrigger.png"
fi

# Create AppStream metadata
cat > "$APPDIR/usr/share/metainfo/whispertrigger.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>io.github.whispertrigger</id>
  <name>WhisperTrigger</name>
  <summary>Speech-to-text application using OpenAI's Whisper</summary>
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
    <category>Utility</category>
    <category>Audio</category>
  </categories>
  <url type="homepage">https://github.com/yourusername/whispertrigger</url>
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
"$APPDIR/usr/bin/whispertrigger" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Create virtual environment and install dependencies
echo "Creating Python virtual environment and installing dependencies..."
python3 -m venv "$APPDIR/usr/lib/venv"
source "$APPDIR/usr/lib/venv/bin/activate"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

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
ARCH=x86_64 "$SCRIPT_DIR/appimagetool-x86_64.AppImage" "$APPDIR" "$SCRIPT_DIR/WhisperTrigger-x86_64.AppImage"

echo "AppImage created: $SCRIPT_DIR/WhisperTrigger-x86_64.AppImage"
echo "You can now distribute this file to other Linux users."
