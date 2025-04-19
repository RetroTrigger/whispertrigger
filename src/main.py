#!/usr/bin/env python3
"""
WhisperTrigger - An open-source Linux speech-to-text application
inspired by SuperWhisper, built with OpenAI's Whisper model.
"""

import sys
import os
import json
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize

from transcription_engine import TranscriptionEngine
from keyboard_listener import KeyboardListener
from settings_dialog import SettingsDialog
from audio_recorder import AudioRecorder
from waveform_widget import WaveformWidget
from processing_modes import ProcessingMode, load_modes

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser("~/.whispertrigger.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WhisperTrigger")

class WhisperTrigger(QApplication):
    """Main application class for WhisperTrigger"""
    
    def __init__(self, args):
        super().__init__(args)
        self.setQuitOnLastWindowClosed(False)
        self.setApplicationName("WhisperTrigger")
        
        # Create config directory if it doesn't exist
        self.config_dir = Path.home() / ".config" / "whispertrigger"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize components
        self.init_components()
        self.init_tray_icon()
        self.init_keyboard_shortcuts()
        
        logger.info("WhisperTrigger initialized successfully")
    
    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Default configuration
        default_config = {
            "model": "base",
            "language": "en",
            "active_mode": "default",
            "hotkeys": {
                "start_stop_recording": "alt+r",
                "transcribe_file": "alt+t",
                "settings": "alt+c",
                "quit": "alt+q"
            },
            "audio": {
                "sample_rate": 16000,
                "chunk_size": 1024,
                "silence_threshold": 500,
                "silence_duration": 1.0
            },
            "ui": {
                "waveform_color": "#00aaff",
                "background_color": "#2e2e2e",
                "text_color": "#ffffff"
            }
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def init_components(self):
        """Initialize application components"""
        # Load processing modes
        self.modes = load_modes(self.config_dir / "modes")
        
        # Initialize transcription engine
        self.engine = TranscriptionEngine(
            model_name=self.config["model"],
            language=self.config["language"]
        )
        
        # Initialize audio recorder
        self.recorder = AudioRecorder(
            sample_rate=self.config["audio"]["sample_rate"],
            chunk_size=self.config["audio"]["chunk_size"],
            silence_threshold=self.config["audio"]["silence_threshold"],
            silence_duration=self.config["audio"]["silence_duration"]
        )
        
        # Initialize waveform widget
        self.waveform = WaveformWidget(
            waveform_color=self.config["ui"]["waveform_color"],
            background_color=self.config["ui"]["background_color"]
        )
        
        # Connect signals
        self.recorder.audio_data_signal.connect(self.waveform.update_waveform)
        self.recorder.recording_finished.connect(self.on_recording_finished)
    
    def init_tray_icon(self):
        """Initialize system tray icon and menu"""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Look for icons in different sizes for better scaling
        icon_sizes = [32, 64, 128, 256]
        icon_paths = {}
        
        # Try multiple possible locations for the icons
        possible_resource_dirs = [
            os.path.join(os.path.dirname(__file__), "../resources"),  # Regular path
            os.path.join(os.path.dirname(__file__), "resources"),     # Direct subdirectory
            "/usr/share/icons/hicolor/256x256/apps",                  # AppImage standard location
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources")),  # AppImage relative path
        ]
        
        # Log possible locations for debugging
        logger.debug(f"Searching for icons in: {possible_resource_dirs}")
        
        for size in icon_sizes:
            icon_found = False
            
            for resource_dir in possible_resource_dirs:
                if size == 256:
                    path = os.path.join(resource_dir, "icon.png")
                    alt_path = os.path.join(resource_dir, "whispertrigger.png")  # AppImage name
                else:
                    path = os.path.join(resource_dir, f"icon_{size}.png")
                    alt_path = os.path.join(resource_dir, f"whispertrigger_{size}.png")  # AppImage name
                
                if os.path.exists(path):
                    icon_paths[size] = path
                    logger.debug(f"Found icon at: {path}")
                    icon_found = True
                    break
                elif os.path.exists(alt_path):
                    icon_paths[size] = alt_path
                    logger.debug(f"Found icon at: {alt_path}")
                    icon_found = True
                    break
            
            if not icon_found:
                logger.warning(f"Could not find icon for size {size}px")
        
        if icon_paths:
            # Create a QIcon with multiple sizes for better scaling
            icon = QIcon()
            for size, path in icon_paths.items():
                icon.addFile(path, QSize(size, size))
                logger.debug(f"Added icon size {size}px from {path}")
            
            self.tray_icon.setIcon(icon)
            logger.info(f"Using custom icon with sizes: {list(icon_paths.keys())}")
            
            # Check if icon was set correctly
            if self.tray_icon.icon().isNull():
                logger.error("Failed to set custom icon - icon is null after setting")
            else:
                logger.debug("Custom icon set successfully")
        else:
            # Use fallback icon
            from PyQt6.QtWidgets import QStyle
            logger.warning("No custom icons found, using fallback icon")
            
            try:
                fallback_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
                self.tray_icon.setIcon(fallback_icon)
                
                if self.tray_icon.icon().isNull():
                    logger.error("Failed to set fallback icon - icon is null after setting")
                else:
                    logger.debug("Fallback icon set successfully")
            except Exception as e:
                logger.error(f"Error setting fallback icon: {e}")
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.error("System tray is not available on this system")
        else:
            logger.debug("System tray is available")
        
        try:
            # Create tray menu
            logger.debug("Creating tray menu")
            tray_menu = QMenu()
            
            # Add actions
            start_action = QAction("Start Recording", self)
            start_action.triggered.connect(self.toggle_recording)
            tray_menu.addAction(start_action)
            logger.debug("Added 'Start Recording' action")
            
            settings_action = QAction("Settings", self)
            settings_action.triggered.connect(self.show_settings)
            tray_menu.addAction(settings_action)
            logger.debug("Added 'Settings' action")
            
            tray_menu.addSeparator()
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit)
            tray_menu.addAction(quit_action)
            logger.debug("Added 'Quit' action")
            
            # Set tray menu
            self.tray_icon.setContextMenu(tray_menu)
            logger.debug("Set tray context menu")
            
            # Make sure the tray icon is visible
            self.tray_icon.show()
            logger.info("Tray icon should now be visible")
            
            # Force the icon to update
            self.tray_icon.setVisible(False)
            self.tray_icon.setVisible(True)
            
        except Exception as e:
            logger.error(f"Error initializing tray menu: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Show startup message
        try:
            if self.tray_icon.isSystemTrayAvailable() and self.tray_icon.supportsMessages():
                logger.debug("Showing startup notification")
                self.tray_icon.showMessage(
                    "WhisperTrigger",
                    "WhisperTrigger is running. Press Alt+R to start recording.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
                logger.debug("Startup notification sent")
            else:
                logger.warning("System tray doesn't support notifications")
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def init_keyboard_shortcuts(self):
        """Initialize global keyboard shortcuts"""
        self.keyboard_listener = KeyboardListener(self.config["hotkeys"])
        self.keyboard_listener.start_stop_recording_triggered.connect(self.toggle_recording)
        self.keyboard_listener.transcribe_file_triggered.connect(self.transcribe_file)
        self.keyboard_listener.settings_triggered.connect(self.show_settings)
        self.keyboard_listener.quit_triggered.connect(self.quit)
        self.keyboard_listener.start()
    
    def toggle_recording(self):
        """Start or stop recording"""
        if self.recorder.is_recording:
            self.recorder.stop_recording()
            self.waveform.hide()
        else:
            self.recorder.start_recording()
            self.waveform.show()
    
    def on_recording_finished(self, audio_file):
        """Handle recording finished event"""
        logger.info(f"Recording finished: {audio_file}")
        self.waveform.hide()
        
        # Start transcription
        self.transcribe_audio(audio_file)
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file"""
        # Get active mode
        active_mode_name = self.config["active_mode"]
        active_mode = self.modes.get(active_mode_name, self.modes.get("default"))
        
        # Start transcription in a separate thread
        self.transcription_thread = TranscriptionThread(
            self.engine,
            audio_file,
            active_mode
        )
        self.transcription_thread.transcription_complete.connect(self.on_transcription_complete)
        self.transcription_thread.start()
        
        # Show processing indicator
        self.tray_icon.showMessage(
            "WhisperTrigger",
            "Processing audio...",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def on_transcription_complete(self, text):
        """Handle transcription complete event"""
        import pyperclip
        
        # Copy text to clipboard
        pyperclip.copy(text)
        
        # Paste text at cursor position
        try:
            os.system("xdotool key ctrl+v")
        except Exception as e:
            logger.error(f"Error pasting text: {e}")
        
        # Show notification
        self.tray_icon.showMessage(
            "WhisperTrigger",
            "Transcription complete and pasted",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def transcribe_file(self):
        """Transcribe a file selected by the user"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Audio or Video File",
            str(Path.home()),
            "Media Files (*.mp3 *.wav *.m4a *.mp4 *.mkv *.avi *.flac *.ogg)"
        )
        
        if file_path:
            self.transcribe_audio(file_path)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.config, self.modes)
        if dialog.exec():
            # Update configuration
            self.config = dialog.get_config()
            self.save_config()
            
            # Reinitialize components if needed
            self.engine.set_model(self.config["model"])
            self.engine.set_language(self.config["language"])
            
            # Update keyboard shortcuts
            self.keyboard_listener.update_hotkeys(self.config["hotkeys"])
    
    def quit(self):
        """Quit the application"""
        # Stop recording if active
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        
        # Stop keyboard listener
        self.keyboard_listener.stop()
        
        # Save configuration
        self.save_config()
        
        # Quit application
        self.tray_icon.hide()
        self.quit()


class TranscriptionThread(QThread):
    """Thread for audio transcription"""
    
    transcription_complete = pyqtSignal(str)
    
    def __init__(self, engine, audio_file, processing_mode):
        super().__init__()
        self.engine = engine
        self.audio_file = audio_file
        self.processing_mode = processing_mode
    
    def run(self):
        """Run transcription"""
        try:
            # Transcribe audio
            raw_text = self.engine.transcribe(self.audio_file)
            
            # Process text according to mode
            processed_text = self.processing_mode.process(raw_text)
            
            # Emit signal with processed text
            self.transcription_complete.emit(processed_text)
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            self.transcription_complete.emit(f"Error: {str(e)}")


if __name__ == "__main__":
    app = WhisperTrigger(sys.argv)
    sys.exit(app.exec())
