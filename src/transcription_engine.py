#!/usr/bin/env python3
"""
TranscriptionEngine - Core speech-to-text functionality using Whisper
"""

import os
import logging
import tempfile
import torch
from faster_whisper import WhisperModel
from pathlib import Path
import ffmpeg

logger = logging.getLogger("WhisperTrigger.TranscriptionEngine")

class TranscriptionEngine:
    """
    Handles audio transcription using OpenAI's Whisper model via faster-whisper.
    Supports multiple model sizes and languages.
    """
    
    # Available model sizes
    MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
    
    def __init__(self, model_name="base", language="en", device=None):
        """
        Initialize the transcription engine with the specified model and language.
        
        Args:
            model_name (str): The Whisper model size to use
            language (str): The language code (e.g., "en" for English)
            device (str, optional): Device to use for inference ("cuda", "cpu", or None for auto)
        """
        self.model_name = model_name
        self.language = language
        
        # Determine the device to use
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Compute type based on device
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        logger.info(f"Initializing Whisper model: {model_name} on {self.device} using {self.compute_type}")
        
        # Initialize the model
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            # Ensure model name is valid
            if self.model_name not in self.MODEL_SIZES:
                logger.warning(f"Invalid model name: {self.model_name}. Using 'base' instead.")
                self.model_name = "base"
            
            # Load the model
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=os.path.expanduser("~/.cache/whispertrigger/models")
            )
            
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def set_model(self, model_name):
        """Change the model size"""
        if model_name != self.model_name:
            self.model_name = model_name
            self._load_model()
    
    def set_language(self, language):
        """Set the language for transcription"""
        self.language = language
    
    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text.
        
        Args:
            audio_file (str): Path to the audio file
        
        Returns:
            str: The transcribed text
        """
        logger.info(f"Transcribing audio file: {audio_file}")
        
        try:
            # Ensure the file exists
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Convert audio to the correct format if needed
            audio_file = self._prepare_audio(audio_file)
            
            # Transcribe the audio
            segments, info = self.model.transcribe(
                audio_file,
                language=self.language,
                task="transcribe",
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments into a single text
            text = " ".join([segment.text for segment in segments])
            
            logger.info(f"Transcription complete: {len(text)} characters")
            return text
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    def _prepare_audio(self, audio_file):
        """
        Prepare audio file for transcription by converting to the correct format.
        
        Args:
            audio_file (str): Path to the audio file
        
        Returns:
            str: Path to the prepared audio file
        """
        # Check if the file is already in the correct format (WAV, 16kHz, mono)
        try:
            probe = ffmpeg.probe(audio_file)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if audio_stream and audio_stream.get('sample_rate') == '16000' and audio_stream.get('channels') == 1:
                return audio_file
            
            # Convert to the correct format
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.close()
            
            logger.info(f"Converting audio file to 16kHz WAV: {audio_file} -> {temp_file.name}")
            
            (
                ffmpeg
                .input(audio_file)
                .output(temp_file.name, acodec='pcm_s16le', ar=16000, ac=1)
                .run(quiet=True, overwrite_output=True)
            )
            
            return temp_file.name
        
        except Exception as e:
            logger.warning(f"Error preparing audio, using original file: {e}")
            return audio_file
    
    def transcribe_realtime(self, audio_chunk, is_final=False):
        """
        Transcribe an audio chunk in real-time.
        
        Args:
            audio_chunk (bytes): Raw audio data
            is_final (bool): Whether this is the final chunk
        
        Returns:
            str: The transcribed text
        """
        # This is a simplified version - real implementation would need
        # to handle streaming and context from previous chunks
        try:
            # Save audio chunk to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_chunk)
                temp_file_path = temp_file.name
            
            # Transcribe the chunk
            text = self.transcribe(temp_file_path)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return text
        
        except Exception as e:
            logger.error(f"Real-time transcription error: {e}")
            return ""
