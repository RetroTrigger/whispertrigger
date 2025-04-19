#!/usr/bin/env python3
"""
WaveformWidget - Provides visual feedback during audio recording
"""

import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRect, QTimer, QPropertyAnimation, QEasingCurve, QPoint

class WaveformWidget(QWidget):
    """
    Displays a waveform visualization of audio data.
    Provides visual feedback during recording with animations and effects.
    """
    
    def __init__(self, waveform_color="#00aaff", background_color="#2e2e2e"):
        """
        Initialize the waveform widget.
        
        Args:
            waveform_color (str): Color of the waveform in hex format
            background_color (str): Color of the background in hex format
        """
        super().__init__()
        
        self.waveform_color = QColor(waveform_color)
        self.background_color = QColor(background_color)
        
        # Audio data for visualization
        self.audio_data = np.zeros(100)
        self.smoothed_data = np.zeros(100)
        self.smoothing_factor = 0.3  # Lower = smoother
        
        # Animation properties
        self._glow_intensity = 0.0  # Initialize with a safe default value
        
        # Create animation manually without using property name
        try:
            self.glow_animation = QPropertyAnimation(self)
            self.glow_animation.setTargetObject(self)
            self.glow_animation.setDuration(1000)
            self.glow_animation.setStartValue(0.0)
            self.glow_animation.setEndValue(1.0)
            self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.glow_animation.setLoopCount(-1)  # Infinite loop
            self.glow_animation.valueChanged.connect(self.set_glow_intensity)
        except Exception as e:
            print(f"Error initializing glow animation: {e}")
            # Provide a dummy animation that won't cause crashes
            self.glow_animation = QPropertyAnimation(self)
        
        # Timer for animation updates
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(30)  # ~33 fps
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        # Set window properties
        self.setWindowTitle("WhisperTrigger Recording")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(400, 200)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add recording label
        self.recording_label = QLabel("Recording...")
        self.recording_label.setStyleSheet(f"color: {self.waveform_color.name()}; font-size: 14px; font-weight: bold;")
        self.recording_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.recording_label)
        
        # Set layout
        self.setLayout(layout)
        
        # Position widget at the bottom center of the screen
        self.position_widget()
        
        # Start animations with error handling
        try:
            if self.glow_animation and not self.glow_animation.state():
                self.glow_animation.start()
        except Exception as e:
            print(f"Error starting glow animation: {e}")
    
    def position_widget(self):
        """Position the widget at the bottom center of the screen"""
        screen_geometry = self.screen().geometry()
        widget_width = 400
        widget_height = 200
        
        x = (screen_geometry.width() - widget_width) // 2
        y = screen_geometry.height() - widget_height - 100  # 100px from bottom
        
        self.setGeometry(x, y, widget_width, widget_height)
    
    def update_waveform(self, audio_data):
        """
        Update the waveform with new audio data.
        
        Args:
            audio_data (np.ndarray): Audio data as numpy array
        """
        # Normalize audio data to range [-1, 1]
        normalized_data = audio_data.astype(np.float32) / 32768.0
        
        # Calculate RMS amplitude
        rms = np.sqrt(np.mean(np.square(normalized_data)))
        
        # Update smoothed data
        if len(self.smoothed_data) != len(normalized_data):
            self.smoothed_data = np.zeros_like(normalized_data)
        
        self.smoothed_data = (self.smoothing_factor * normalized_data + 
                             (1 - self.smoothing_factor) * self.smoothed_data)
        
        # Store data for visualization
        self.audio_data = self.smoothed_data
        
        # Update glow based on audio level
        glow_value = min(1.0, rms * 5.0)  # Scale RMS to [0, 1]
        self.glow_animation.setStartValue(glow_value * 0.3)
        self.glow_animation.setEndValue(glow_value)
        
        # Update recording time
        elapsed_time = self.recording_time()
        self.recording_label.setText(f"Recording... {elapsed_time}")
    
    def recording_time(self):
        """
        Calculate and format the recording time.
        
        Returns:
            str: Formatted recording time (MM:SS)
        """
        # Get elapsed time since widget was shown
        elapsed_ms = self.animation_timer.interval() * self.animation_timer.remainingTime()
        
        # Format as MM:SS
        seconds = int(elapsed_ms / 1000) % 60
        minutes = int(elapsed_ms / 60000)
        
        return f"{minutes:02d}:{seconds:02d}"
    
    def paintEvent(self, event):
        """
        Paint the waveform visualization.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with rounded corners
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.background_color))
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        # Draw waveform
        self.draw_waveform(painter)
    
    def draw_waveform(self, painter):
        """
        Draw the waveform visualization.
        
        Args:
            painter (QPainter): QPainter instance
        """
        if len(self.audio_data) == 0:
            return
        
        # Calculate dimensions
        width = self.width() - 40  # 20px margin on each side
        height = self.height() - 80  # 40px margin on top and bottom, plus label height
        center_y = self.height() // 2 + 10  # Offset for label
        
        # Create gradient for waveform
        gradient = QLinearGradient(0, center_y - height // 2, 0, center_y + height // 2)
        gradient.setColorAt(0, self.waveform_color.lighter(150))
        gradient.setColorAt(0.5, self.waveform_color)
        gradient.setColorAt(1, self.waveform_color.darker(150))
        
        # Draw waveform bars
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        
        # Number of bars to draw
        num_bars = min(100, len(self.audio_data))
        bar_width = width / num_bars
        
        for i in range(num_bars):
            # Get amplitude for this bar
            amplitude = abs(self.audio_data[i % len(self.audio_data)])
            
            # Calculate bar height (scale amplitude)
            bar_height = amplitude * height
            
            # Calculate bar position
            x = 20 + i * bar_width
            y = center_y - bar_height / 2
            
            # Draw bar
            painter.drawRoundedRect(
                QRect(int(x), int(y), int(bar_width * 0.8), int(bar_height)),
                2, 2
            )
        
        # Draw glow effect
        self.draw_glow(painter, width, height, center_y)
    
    def draw_glow(self, painter, width, height, center_y):
        """
        Draw a glow effect around the waveform.
        
        Args:
            painter (QPainter): QPainter instance
            width (int): Width of the drawing area
            height (int): Height of the drawing area
            center_y (int): Y-coordinate of the center
        """
        # Set up glow pen
        glow_color = QColor(self.waveform_color)
        
        # Safety check to prevent NoneType error
        intensity = self.glow_intensity if self.glow_intensity is not None else 0.0
        glow_color.setAlpha(int(50 * intensity))
        
        glow_pen = QPen(glow_color)
        glow_pen.setWidth(10)
        painter.setPen(glow_pen)
        
        # Draw glow outline
        painter.drawRoundedRect(
            20, center_y - height // 2 - 5,
            width, height + 10,
            10, 10
        )
    
    def get_glow_intensity(self):
        """Get the glow intensity property"""
        # Ensure we never return None
        return 0.0 if self._glow_intensity is None else self._glow_intensity
    
    def set_glow_intensity(self, intensity):
        """Set the glow intensity property"""
        # Ensure we never set None
        self._glow_intensity = 0.0 if intensity is None else float(intensity)
        self.update()
    
    # Define property for animation
    glow_intensity = property(get_glow_intensity, set_glow_intensity)
    
    def closeEvent(self, event):
        """Handle close event"""
        # Stop animations
        self.glow_animation.stop()
        self.animation_timer.stop()
        super().closeEvent(event)
