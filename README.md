# WhisperTrigger

An open-source Linux speech-to-text application inspired by SuperWhisper, built with OpenAI's Whisper model.

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

## Requirements

- Linux operating system
- Python 3.8+
- CUDA-compatible GPU (optional, for faster processing)
- FFmpeg

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whispertrigger.git
cd whispertrigger
```

2. Install dependencies:
```bash
# Install system dependencies
sudo apt-get install python3-dev python3-pip ffmpeg portaudio19-dev python3-pyaudio xdotool

# Install Python dependencies
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/main.py
```

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

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The core speech recognition model
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
