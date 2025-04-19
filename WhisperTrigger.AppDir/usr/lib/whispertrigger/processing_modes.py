#!/usr/bin/env python3
"""
ProcessingMode - Handles different text processing modes for transcription
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("WhisperTrigger.ProcessingModes")

class ProcessingMode:
    """
    Represents a processing mode for transcribed text.
    Each mode has a name, description, and instructions for processing.
    """
    
    def __init__(self, name, description, instructions):
        """
        Initialize a processing mode.
        
        Args:
            name (str): Name of the mode
            description (str): Description of the mode
            instructions (str): Instructions for processing
        """
        self.name = name
        self.description = description
        self.instructions = instructions
    
    def process(self, text):
        """
        Process the transcribed text according to the mode's instructions.
        
        Args:
            text (str): The transcribed text to process
        
        Returns:
            str: The processed text
        """
        # In a full implementation, this would use a language model to process the text
        # based on the instructions. For now, we'll just return the text as is.
        
        # Basic processing - capitalize sentences and add periods if missing
        processed_text = text.strip()
        
        # Capitalize first letter of sentences
        if processed_text and len(processed_text) > 0:
            processed_text = processed_text[0].upper() + processed_text[1:]
        
        # Add period at the end if missing
        if processed_text and not processed_text.endswith(('.', '!', '?')):
            processed_text += '.'
        
        return processed_text
    
    def to_dict(self):
        """
        Convert the mode to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the mode
        """
        return {
            'name': self.name,
            'description': self.description,
            'instructions': self.instructions
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a mode from a dictionary.
        
        Args:
            data (dict): Dictionary representation of the mode
        
        Returns:
            ProcessingMode: The created mode
        """
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            instructions=data.get('instructions', '')
        )


def load_modes(modes_dir):
    """
    Load processing modes from the specified directory.
    
    Args:
        modes_dir (Path): Directory containing mode files
    
    Returns:
        dict: Dictionary mapping mode names to ProcessingMode objects
    """
    modes = {}
    
    # Create default mode
    default_mode = ProcessingMode(
        name="default",
        description="Default processing mode",
        instructions="Process the transcribed text as follows:\n\n1. Correct any grammar or spelling errors\n2. Format the text properly with punctuation\n3. Return the processed text"
    )
    modes["default"] = default_mode
    
    # Create formatting mode
    formatting_mode = ProcessingMode(
        name="formatting",
        description="Format text with proper capitalization and punctuation",
        instructions="Process the transcribed text as follows:\n\n1. Capitalize the first letter of each sentence\n2. Add proper punctuation\n3. Format lists and paragraphs\n4. Do not change the content or meaning"
    )
    modes["formatting"] = formatting_mode
    
    # Create raw mode
    raw_mode = ProcessingMode(
        name="raw",
        description="Raw transcription without processing",
        instructions="Return the transcribed text exactly as is, without any processing or modifications."
    )
    modes["raw"] = raw_mode
    
    # Create notes mode
    notes_mode = ProcessingMode(
        name="notes",
        description="Format as meeting notes",
        instructions="Process the transcribed text as follows:\n\n1. Format as meeting notes\n2. Add bullet points for key items\n3. Organize into sections if multiple topics are discussed\n4. Highlight action items and decisions"
    )
    modes["notes"] = notes_mode
    
    # Create email mode
    email_mode = ProcessingMode(
        name="email",
        description="Format as a professional email",
        instructions="Process the transcribed text as follows:\n\n1. Format as a professional email\n2. Add appropriate greeting and closing\n3. Organize content into clear paragraphs\n4. Maintain a professional tone"
    )
    modes["email"] = email_mode
    
    # Create code mode
    code_mode = ProcessingMode(
        name="code",
        description="Format as code or technical content",
        instructions="Process the transcribed text as follows:\n\n1. Format as code or technical documentation\n2. Preserve code syntax and structure\n3. Use proper technical terminology\n4. Format variable names and functions correctly"
    )
    modes["code"] = code_mode
    
    # Ensure modes directory exists
    os.makedirs(modes_dir, exist_ok=True)
    
    # Load custom modes from files
    try:
        for file_path in modes_dir.glob('*.json'):
            try:
                with open(file_path, 'r') as f:
                    mode_data = json.load(f)
                
                mode = ProcessingMode.from_dict(mode_data)
                modes[mode.name] = mode
                logger.info(f"Loaded mode: {mode.name}")
            except Exception as e:
                logger.error(f"Error loading mode from {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error loading modes: {e}")
    
    return modes


def save_modes(modes, modes_dir):
    """
    Save processing modes to the specified directory.
    
    Args:
        modes (dict): Dictionary mapping mode names to ProcessingMode objects
        modes_dir (Path): Directory to save mode files
    """
    # Ensure modes directory exists
    os.makedirs(modes_dir, exist_ok=True)
    
    # Save each mode to a file
    for name, mode in modes.items():
        try:
            file_path = modes_dir / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(mode.to_dict(), f, indent=4)
            
            logger.info(f"Saved mode: {name}")
        except Exception as e:
            logger.error(f"Error saving mode {name}: {e}")
