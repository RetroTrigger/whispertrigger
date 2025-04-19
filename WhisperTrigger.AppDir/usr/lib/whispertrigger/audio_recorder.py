#!/usr/bin/env python3
"""
AudioRecorder - Handles audio recording from microphone
"""

import os
import time
import wave
import logging
import tempfile
import threading
import numpy as np
import sounddevice as sd
import pyaudio
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger("WhisperTrigger.AudioRecorder")

class AudioRecorder(QObject):
    """
    Records audio from the microphone and saves it to a file.
    Emits signals with audio data for visualization and when recording is finished.
    """
    
    # Signal emitted with audio data for visualization
    audio_data_signal = pyqtSignal(np.ndarray)
    
    # Signal emitted when recording is finished with path to audio file
    recording_finished = pyqtSignal(str)
    
    def __init__(self, sample_rate=16000, chunk_size=1024, silence_threshold=500, silence_duration=1.0):
        """
        Initialize the audio recorder.
        
        Args:
            sample_rate (int): Sample rate in Hz
            chunk_size (int): Number of frames per buffer
            silence_threshold (int): Threshold for silence detection
            silence_duration (float): Duration of silence to stop recording (in seconds)
        """
        super().__init__()
        
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        
        self.is_recording = False
        self.audio_data = []
        self.temp_dir = os.path.join(tempfile.gettempdir(), "whispertrigger")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # PyAudio instance
        self.p = pyaudio.PyAudio()
        
        # Find the default input device
        self.input_device_index = self._get_default_input_device()
    
    def _get_default_input_device(self):
        """Get the default input device index"""
        try:
            # Get default input device info
            info = self.p.get_default_input_device_info()
            return info['index']
        except Exception as e:
            logger.warning(f"Could not get default input device: {e}")
            # Try to find any input device
            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    logger.info(f"Using input device: {info['name']}")
                    return i
            
            logger.error("No input device found")
            return None
    
    def start_recording(self):
        """Start recording audio from the microphone"""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        if self.input_device_index is None:
            logger.error("No input device available")
            return
        
        logger.info("Starting audio recording")
        
        self.is_recording = True
        self.audio_data = []
        self.silent_chunks = 0
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self):
        """Stop recording audio"""
        if not self.is_recording:
            logger.warning("Not recording")
            return
        
        logger.info("Stopping audio recording")
        self.is_recording = False
        
        # Wait for recording thread to finish
        if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
    
    def _record_audio(self):
        """Record audio from the microphone"""
        try:
            # Open audio stream
            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Audio stream opened")
            
            # Record audio until stopped or silence detected
            self.silent_chunks = 0
            
            while self.is_recording:
                # Read audio data
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
                
                # Convert to numpy array for visualization
                audio_array = np.frombuffer(data, dtype=np.int16)
                
                # Emit signal with audio data for visualization
                self.audio_data_signal.emit(audio_array)
                
                # Check for silence
                if self._is_silent(audio_array):
                    self.silent_chunks += 1
                    if self.silent_chunks >= int(self.silence_duration * self.sample_rate / self.chunk_size):
                        logger.info("Silence detected, stopping recording")
                        self.is_recording = False
                else:
                    self.silent_chunks = 0
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
            # Save audio to file
            audio_file = self._save_audio()
            
            # Emit signal with audio file path
            self.recording_finished.emit(audio_file)
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            self.is_recording = False
    
    def _is_silent(self, audio_array):
        """
        Check if audio chunk is silent.
        
        Args:
            audio_array (np.ndarray): Audio data as numpy array
        
        Returns:
            bool: True if audio is silent, False otherwise
        """
        # Calculate RMS amplitude
        rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float32))))
        
        # Check if below threshold
        return rms < self.silence_threshold
    
    def _save_audio(self):
        """
        Save recorded audio to a WAV file.
        
        Returns:
            str: Path to the saved audio file
        """
        if not self.audio_data:
            logger.warning("No audio data to save")
            return None
        
        # Create a temporary file
        timestamp = int(time.time())
        audio_file = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
        
        logger.info(f"Saving audio to {audio_file}")
        
        try:
            # Save audio data to WAV file
            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.audio_data))
            
            return audio_file
        
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return None
    
    def __del__(self):
        """Clean up PyAudio instance"""
        if hasattr(self, 'p'):
            self.p.terminate()
