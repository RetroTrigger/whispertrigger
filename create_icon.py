#!/usr/bin/env python3
"""
Script to create a custom icon for WhisperTrigger
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(output_path, size=256):
    """Create a custom icon for WhisperTrigger"""
    # Create a new image with transparent background
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Define colors
    bg_color = (52, 152, 219)  # Blue
    mic_color = (236, 240, 241)  # White/Light gray
    wave_color = (231, 76, 60)  # Red
    
    # Draw circular background
    padding = size // 10
    draw.ellipse(
        [(padding, padding), (size - padding, size - padding)],
        fill=bg_color
    )
    
    # Draw microphone
    mic_width = size // 3
    mic_height = size // 2
    mic_top = size // 4
    mic_left = (size - mic_width) // 2
    
    # Microphone body
    draw.rounded_rectangle(
        [(mic_left, mic_top), (mic_left + mic_width, mic_top + mic_height)],
        radius=mic_width // 3,
        fill=mic_color
    )
    
    # Microphone base
    base_width = mic_width * 1.2
    base_height = size // 10
    base_top = mic_top + mic_height
    base_left = (size - base_width) // 2
    draw.rounded_rectangle(
        [(base_left, base_top), (base_left + base_width, base_top + base_height)],
        radius=base_height // 2,
        fill=mic_color
    )
    
    # Draw sound waves
    wave_padding = size // 5
    wave_top = size // 3
    wave_height = size // 3
    
    # Left wave
    draw.arc(
        [(wave_padding, wave_top), (size // 2, wave_top + wave_height)],
        start=270, end=0,
        fill=wave_color,
        width=size // 40
    )
    
    # Right wave
    draw.arc(
        [(size // 2, wave_top), (size - wave_padding, wave_top + wave_height)],
        start=180, end=270,
        fill=wave_color,
        width=size // 40
    )
    
    # Save the icon
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    icon.save(output_path)
    print(f"Icon created at {output_path}")

if __name__ == "__main__":
    # Create icons in different sizes
    create_icon("resources/icon.png", 256)
    create_icon("resources/icon_128.png", 128)
    create_icon("resources/icon_64.png", 64)
    create_icon("resources/icon_32.png", 32)
