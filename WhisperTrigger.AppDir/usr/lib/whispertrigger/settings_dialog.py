#!/usr/bin/env python3
"""
SettingsDialog - Dialog for configuring application settings
"""

import os
import json
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QComboBox, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout,
    QDialogButtonBox, QColorDialog, QFileDialog, QTextEdit
)
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtCore import Qt

logger = logging.getLogger("WhisperTrigger.SettingsDialog")

class SettingsDialog(QDialog):
    """
    Dialog for configuring application settings.
    Provides tabs for general settings, audio settings, model settings,
    keyboard shortcuts, and processing modes.
    """
    
    def __init__(self, config, modes):
        """
        Initialize the settings dialog.
        
        Args:
            config (dict): Current configuration
            modes (dict): Available processing modes
        """
        super().__init__()
        
        self.config = config.copy()
        self.modes = modes
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        # Set window properties
        self.setWindowTitle("WhisperTrigger Settings")
        self.setMinimumSize(600, 500)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_audio_tab(), "Audio")
        self.tab_widget.addTab(self.create_model_tab(), "Model")
        self.tab_widget.addTab(self.create_shortcuts_tab(), "Shortcuts")
        self.tab_widget.addTab(self.create_modes_tab(), "Modes")
        
        layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def create_general_tab(self):
        """Create the general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Language selection
        language_group = QGroupBox("Language")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        languages = [
            ("en", "English"),
            ("fr", "French"),
            ("de", "German"),
            ("es", "Spanish"),
            ("it", "Italian"),
            ("pt", "Portuguese"),
            ("nl", "Dutch"),
            ("ja", "Japanese"),
            ("zh", "Chinese"),
            ("ru", "Russian"),
            ("ar", "Arabic"),
            ("hi", "Hindi"),
            ("ko", "Korean")
        ]
        
        for code, name in languages:
            self.language_combo.addItem(name, code)
        
        # Set current language
        current_lang = self.config.get("language", "en")
        for i, (code, _) in enumerate(languages):
            if code == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
        
        language_layout.addRow("Transcription Language:", self.language_combo)
        language_group.setLayout(language_layout)
        layout.addWidget(language_group)
        
        # UI settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout()
        
        # Waveform color
        self.waveform_color_btn = QPushButton()
        self.waveform_color = QColor(self.config["ui"]["waveform_color"])
        self.waveform_color_btn.setStyleSheet(
            f"background-color: {self.waveform_color.name()}; min-width: 60px;"
        )
        self.waveform_color_btn.clicked.connect(self.choose_waveform_color)
        ui_layout.addRow("Waveform Color:", self.waveform_color_btn)
        
        # Background color
        self.bg_color_btn = QPushButton()
        self.bg_color = QColor(self.config["ui"]["background_color"])
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self.bg_color.name()}; min-width: 60px;"
        )
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        ui_layout.addRow("Background Color:", self.bg_color_btn)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Add spacer
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_audio_tab(self):
        """Create the audio settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Audio settings
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QFormLayout()
        
        # Sample rate
        self.sample_rate_combo = QComboBox()
        sample_rates = [8000, 16000, 22050, 44100, 48000]
        for rate in sample_rates:
            self.sample_rate_combo.addItem(f"{rate} Hz", rate)
        
        # Set current sample rate
        current_rate = self.config["audio"]["sample_rate"]
        for i, rate in enumerate(sample_rates):
            if rate == current_rate:
                self.sample_rate_combo.setCurrentIndex(i)
                break
        
        audio_layout.addRow("Sample Rate:", self.sample_rate_combo)
        
        # Chunk size
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(256, 4096)
        self.chunk_size_spin.setSingleStep(256)
        self.chunk_size_spin.setValue(self.config["audio"]["chunk_size"])
        audio_layout.addRow("Chunk Size:", self.chunk_size_spin)
        
        # Silence threshold
        self.silence_threshold_spin = QSpinBox()
        self.silence_threshold_spin.setRange(100, 2000)
        self.silence_threshold_spin.setSingleStep(50)
        self.silence_threshold_spin.setValue(self.config["audio"]["silence_threshold"])
        audio_layout.addRow("Silence Threshold:", self.silence_threshold_spin)
        
        # Silence duration
        self.silence_duration_spin = QDoubleSpinBox()
        self.silence_duration_spin.setRange(0.5, 5.0)
        self.silence_duration_spin.setSingleStep(0.1)
        self.silence_duration_spin.setValue(self.config["audio"]["silence_duration"])
        self.silence_duration_spin.setSuffix(" seconds")
        audio_layout.addRow("Silence Duration:", self.silence_duration_spin)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Add spacer
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_model_tab(self):
        """Create the model settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Model settings
        model_group = QGroupBox("Whisper Model")
        model_layout = QFormLayout()
        
        # Model size
        self.model_combo = QComboBox()
        models = [
            ("tiny", "Tiny (fast, less accurate)"),
            ("base", "Base (balanced)"),
            ("small", "Small (accurate, slower)"),
            ("medium", "Medium (more accurate, slower)"),
            ("large-v2", "Large v2 (most accurate, slowest)"),
            ("large-v3", "Large v3 (most accurate, slowest)")
        ]
        
        for code, name in models:
            self.model_combo.addItem(name, code)
        
        # Set current model
        current_model = self.config.get("model", "base")
        for i, (code, _) in enumerate(models):
            if code == current_model:
                self.model_combo.setCurrentIndex(i)
                break
        
        model_layout.addRow("Model Size:", self.model_combo)
        
        # Device selection
        self.device_combo = QComboBox()
        self.device_combo.addItem("Auto (recommended)", None)
        self.device_combo.addItem("CPU", "cpu")
        self.device_combo.addItem("CUDA (NVIDIA GPU)", "cuda")
        
        # Set current device
        current_device = self.config.get("device", None)
        if current_device == "cpu":
            self.device_combo.setCurrentIndex(1)
        elif current_device == "cuda":
            self.device_combo.setCurrentIndex(2)
        else:
            self.device_combo.setCurrentIndex(0)
        
        model_layout.addRow("Compute Device:", self.device_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Model info
        info_group = QGroupBox("Model Information")
        info_layout = QVBoxLayout()
        
        info_text = (
            "<p><b>Model Size Guide:</b></p>"
            "<ul>"
            "<li><b>Tiny:</b> ~75MB, fastest, less accurate</li>"
            "<li><b>Base:</b> ~150MB, good balance of speed and accuracy</li>"
            "<li><b>Small:</b> ~500MB, more accurate, slower</li>"
            "<li><b>Medium:</b> ~1.5GB, high accuracy, slower</li>"
            "<li><b>Large:</b> ~3GB, highest accuracy, slowest</li>"
            "</ul>"
            "<p>Larger models require more memory and processing power, but provide better transcription quality.</p>"
        )
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Add spacer
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_shortcuts_tab(self):
        """Create the keyboard shortcuts tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Shortcuts group
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QFormLayout()
        
        # Start/stop recording shortcut
        self.recording_shortcut = QLineEdit(self.config["hotkeys"]["start_stop_recording"])
        shortcuts_layout.addRow("Start/Stop Recording:", self.recording_shortcut)
        
        # Transcribe file shortcut
        self.transcribe_shortcut = QLineEdit(self.config["hotkeys"]["transcribe_file"])
        shortcuts_layout.addRow("Transcribe File:", self.transcribe_shortcut)
        
        # Settings shortcut
        self.settings_shortcut = QLineEdit(self.config["hotkeys"]["settings"])
        shortcuts_layout.addRow("Open Settings:", self.settings_shortcut)
        
        # Quit shortcut
        self.quit_shortcut = QLineEdit(self.config["hotkeys"]["quit"])
        shortcuts_layout.addRow("Quit Application:", self.quit_shortcut)
        
        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)
        
        # Shortcut info
        info_group = QGroupBox("Shortcut Format")
        info_layout = QVBoxLayout()
        
        info_text = (
            "<p>Enter shortcuts in the format: <code>modifier+key</code></p>"
            "<p>Examples:</p>"
            "<ul>"
            "<li><code>alt+r</code> - Alt key plus R</li>"
            "<li><code>ctrl+shift+t</code> - Control key plus Shift key plus T</li>"
            "</ul>"
            "<p>Available modifiers: <code>ctrl</code>, <code>alt</code>, <code>shift</code>, <code>super</code> (Windows/Command key)</p>"
        )
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Add spacer
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_modes_tab(self):
        """Create the processing modes tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Active mode selection
        active_mode_group = QGroupBox("Active Mode")
        active_mode_layout = QFormLayout()
        
        self.active_mode_combo = QComboBox()
        
        # Add available modes
        for mode_name in self.modes.keys():
            self.active_mode_combo.addItem(mode_name)
        
        # Set current mode
        current_mode = self.config.get("active_mode", "default")
        for i, mode_name in enumerate(self.modes.keys()):
            if mode_name == current_mode:
                self.active_mode_combo.setCurrentIndex(i)
                break
        
        active_mode_layout.addRow("Current Mode:", self.active_mode_combo)
        active_mode_group.setLayout(active_mode_layout)
        layout.addWidget(active_mode_group)
        
        # Mode editor
        editor_group = QGroupBox("Mode Editor")
        editor_layout = QVBoxLayout()
        
        # Mode selection and controls
        mode_controls_layout = QHBoxLayout()
        
        self.edit_mode_combo = QComboBox()
        for mode_name in self.modes.keys():
            self.edit_mode_combo.addItem(mode_name)
        self.edit_mode_combo.currentIndexChanged.connect(self.load_mode_for_editing)
        
        mode_controls_layout.addWidget(QLabel("Edit Mode:"))
        mode_controls_layout.addWidget(self.edit_mode_combo)
        
        # Add buttons
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.create_new_mode)
        mode_controls_layout.addWidget(new_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_current_mode)
        mode_controls_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_current_mode)
        mode_controls_layout.addWidget(delete_btn)
        
        editor_layout.addLayout(mode_controls_layout)
        
        # Mode name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.mode_name_edit = QLineEdit()
        name_layout.addWidget(self.mode_name_edit)
        editor_layout.addLayout(name_layout)
        
        # Mode description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.mode_desc_edit = QLineEdit()
        desc_layout.addWidget(self.mode_desc_edit)
        editor_layout.addLayout(desc_layout)
        
        # Mode instructions
        editor_layout.addWidget(QLabel("Processing Instructions:"))
        self.mode_instructions_edit = QTextEdit()
        editor_layout.addWidget(self.mode_instructions_edit)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        # Load the first mode for editing
        if self.modes:
            self.load_mode_for_editing(0)
        
        tab.setLayout(layout)
        return tab
    
    def choose_waveform_color(self):
        """Open color dialog to choose waveform color"""
        color = QColorDialog.getColor(self.waveform_color, self, "Choose Waveform Color")
        if color.isValid():
            self.waveform_color = color
            self.waveform_color_btn.setStyleSheet(
                f"background-color: {color.name()}; min-width: 60px;"
            )
    
    def choose_bg_color(self):
        """Open color dialog to choose background color"""
        color = QColorDialog.getColor(self.bg_color, self, "Choose Background Color")
        if color.isValid():
            self.bg_color = color
            self.bg_color_btn.setStyleSheet(
                f"background-color: {color.name()}; min-width: 60px;"
            )
    
    def load_mode_for_editing(self, index):
        """
        Load a mode for editing.
        
        Args:
            index (int): Index of the mode in the combo box
        """
        if index < 0 or not self.modes:
            return
        
        mode_name = self.edit_mode_combo.itemText(index)
        mode = self.modes.get(mode_name)
        
        if mode:
            self.mode_name_edit.setText(mode_name)
            self.mode_desc_edit.setText(mode.description)
            self.mode_instructions_edit.setText(mode.instructions)
    
    def create_new_mode(self):
        """Create a new processing mode"""
        # Generate a unique name
        base_name = "new_mode"
        name = base_name
        counter = 1
        
        while name in self.modes:
            name = f"{base_name}_{counter}"
            counter += 1
        
        # Create a new mode
        from processing_modes import ProcessingMode
        self.modes[name] = ProcessingMode(
            name=name,
            description="New processing mode",
            instructions="Process the transcribed text as follows:\n\n1. Correct any grammar or spelling errors\n2. Format the text properly with punctuation\n3. Return the processed text"
        )
        
        # Add to combo boxes
        self.edit_mode_combo.addItem(name)
        self.active_mode_combo.addItem(name)
        
        # Select the new mode
        self.edit_mode_combo.setCurrentText(name)
        
        # Load for editing
        self.load_mode_for_editing(self.edit_mode_combo.currentIndex())
    
    def save_current_mode(self):
        """Save the current mode being edited"""
        current_index = self.edit_mode_combo.currentIndex()
        if current_index < 0:
            return
        
        old_name = self.edit_mode_combo.itemText(current_index)
        new_name = self.mode_name_edit.text()
        
        # Check if name is valid
        if not new_name:
            return
        
        # Create/update mode
        from processing_modes import ProcessingMode
        mode = ProcessingMode(
            name=new_name,
            description=self.mode_desc_edit.text(),
            instructions=self.mode_instructions_edit.toPlainText()
        )
        
        # Handle name change
        if old_name != new_name:
            # Remove old mode
            if old_name in self.modes:
                del self.modes[old_name]
            
            # Update combo boxes
            self.edit_mode_combo.setItemText(current_index, new_name)
            
            # Find and update in active mode combo
            for i in range(self.active_mode_combo.count()):
                if self.active_mode_combo.itemText(i) == old_name:
                    self.active_mode_combo.setItemText(i, new_name)
                    break
        
        # Save mode
        self.modes[new_name] = mode
    
    def delete_current_mode(self):
        """Delete the current mode being edited"""
        current_index = self.edit_mode_combo.currentIndex()
        if current_index < 0:
            return
        
        mode_name = self.edit_mode_combo.itemText(current_index)
        
        # Don't delete default mode
        if mode_name == "default":
            return
        
        # Remove from modes
        if mode_name in self.modes:
            del self.modes[mode_name]
        
        # Remove from combo boxes
        self.edit_mode_combo.removeItem(current_index)
        
        # Find and remove from active mode combo
        for i in range(self.active_mode_combo.count()):
            if self.active_mode_combo.itemText(i) == mode_name:
                self.active_mode_combo.removeItem(i)
                break
        
        # Load another mode if available
        if self.edit_mode_combo.count() > 0:
            self.load_mode_for_editing(0)
    
    def get_config(self):
        """
        Get the updated configuration.
        
        Returns:
            dict: Updated configuration
        """
        # Update configuration
        self.config["model"] = self.model_combo.currentData()
        self.config["language"] = self.language_combo.currentData()
        self.config["active_mode"] = self.active_mode_combo.currentText()
        self.config["device"] = self.device_combo.currentData()
        
        # Update hotkeys
        self.config["hotkeys"]["start_stop_recording"] = self.recording_shortcut.text()
        self.config["hotkeys"]["transcribe_file"] = self.transcribe_shortcut.text()
        self.config["hotkeys"]["settings"] = self.settings_shortcut.text()
        self.config["hotkeys"]["quit"] = self.quit_shortcut.text()
        
        # Update audio settings
        self.config["audio"]["sample_rate"] = self.sample_rate_combo.currentData()
        self.config["audio"]["chunk_size"] = self.chunk_size_spin.value()
        self.config["audio"]["silence_threshold"] = self.silence_threshold_spin.value()
        self.config["audio"]["silence_duration"] = self.silence_duration_spin.value()
        
        # Update UI settings
        self.config["ui"]["waveform_color"] = self.waveform_color.name()
        self.config["ui"]["background_color"] = self.bg_color.name()
        
        return self.config
