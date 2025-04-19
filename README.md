# WhisperTrigger

An open-source Linux speech-to-text application inspired by SuperWhisper, built with OpenAI's Whisper model. Now available as a standalone AppImage for easy installation!

## Features

- Real-time speech-to-text transcription
- Intelligent text formatting modes
- Global keyboard shortcuts for hands-free operation
- Context-aware AI processing
- File transcription (audio and video)
- Multi-language support
- Visual feedback with audio waveform visualization
- Multiple Whisper model options (tiny, base, small, medium, large)
- Clipboard integration
- Customizable AI processing instructions
- Offline operation with local models
- **NEW:** Standalone AppImage packaging for easy distribution
- **NEW:** Custom system tray icon with visual feedback
- **NEW:** Automatic GPU detection with CPU fallback support
- **NEW:** Improved desktop integration

## Requirements

- Linux operating system
- Python 3.8+
- CUDA-compatible GPU (optional, for faster processing)
- FFmpeg

## Installation

### Method 1: AppImage (Recommended)

1. Download the latest WhisperTrigger AppImage from the [Releases](https://github.com/RetroTrigger/whispertrigger/releases) page.

2. Make the AppImage executable:
```bash
chmod +x WhisperTrigger-x86_64.AppImage
```

3. Run the application:
```bash
./WhisperTrigger-x86_64.AppImage
```

The AppImage contains all necessary dependencies and will automatically detect if you have an NVIDIA GPU for faster processing.

### Method 2: From Source

1. Clone the repository:
```bash
git clone https://github.com/RetroTrigger/whispertrigger.git
cd whispertrigger
```

2. Run the launch script (automatically installs dependencies):
```bash
./launch.sh
```

### Building Your Own AppImage

If you want to build your own AppImage:

1. Clone the repository:
```bash
git clone https://github.com/RetroTrigger/whispertrigger.git
cd whispertrigger
```

2. Run the build script:
```bash
./build_appimage.sh
```

This will create a `WhisperTrigger-x86_64.AppImage` file in the project directory.

## Usage

- Press `Alt+R` to start/stop recording
- Press `Alt+T` to transcribe the last audio file
- Press `Alt+C` to configure settings
- Press `Alt+Q` to quit the application

## Configuration

WhisperTrigger can be configured through the settings dialog or by editing the `config.json` file:

- Model size (tiny, base, small, medium, large)
- Language
- Processing modes
- Keyboard shortcuts
- Audio settings
- AI processing instructions
- GPU/CPU processing options

### Hardware Detection

WhisperTrigger automatically detects if you have an NVIDIA GPU and will use it for faster processing if available. If no compatible GPU is found, it will fall back to CPU processing automatically.

### Custom Tray Icon

The application includes a custom tray icon generator that creates a microphone icon with sound waves. The icon is automatically generated in multiple sizes (32px, 64px, 128px, 256px) for optimal display across different desktop environments.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Troubleshooting

### Tray Icon Not Showing

If the tray icon doesn't appear:

1. Make sure your desktop environment supports system tray icons
2. Try running the test script: `python test_tray_icon.py`
3. Check the application logs for any error messages

### GPU Not Detected

If your NVIDIA GPU is not being detected:

1. Ensure you have the NVIDIA drivers installed: `nvidia-smi`
2. Make sure CUDA is properly set up
3. Try running with the CPU-only option: `./launch.sh --cpu`

### AppImage Issues

If the AppImage doesn't run:

1. Make sure it's executable: `chmod +x WhisperTrigger-x86_64.AppImage`
2. Check if you have FUSE installed: `sudo apt-get install libfuse2`
3. Try extracting the AppImage: `./WhisperTrigger-x86_64.AppImage --appimage-extract`

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The core speech recognition model
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [AppImageKit](https://github.com/AppImage/AppImageKit) - AppImage packaging tools
- [Pillow](https://python-pillow.org/) - Python Imaging Library for icon generation
