#!/usr/bin/env python3
"""
KeyboardListener - Handles global keyboard shortcuts
"""

import logging
import threading
from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger("WhisperTrigger.KeyboardListener")

class KeyboardListener(QObject):
    """
    Listens for global keyboard shortcuts and emits signals when they are pressed.
    Uses pynput to capture keyboard events system-wide.
    """
    
    # Signals emitted when keyboard shortcuts are triggered
    start_stop_recording_triggered = pyqtSignal()
    transcribe_file_triggered = pyqtSignal()
    settings_triggered = pyqtSignal()
    quit_triggered = pyqtSignal()
    
    def __init__(self, hotkeys):
        """
        Initialize the keyboard listener with the specified hotkeys.
        
        Args:
            hotkeys (dict): Dictionary mapping actions to keyboard shortcuts
        """
        super().__init__()
        
        self.hotkeys = hotkeys
        self.listener = None
        self.is_running = False
        
        # Parse hotkeys
        self.hotkey_combinations = self._parse_hotkeys(hotkeys)
        
        # Currently pressed keys
        self.current_keys = set()
    
    def _parse_hotkeys(self, hotkeys):
        """
        Parse hotkey strings into key combinations.
        
        Args:
            hotkeys (dict): Dictionary mapping actions to keyboard shortcuts
        
        Returns:
            dict: Dictionary mapping actions to key combinations
        """
        combinations = {}
        
        for action, hotkey_str in hotkeys.items():
            keys = []
            for key in hotkey_str.lower().split('+'):
                if key == 'ctrl':
                    keys.append(keyboard.Key.ctrl)
                elif key == 'alt':
                    keys.append(keyboard.Key.alt)
                elif key == 'shift':
                    keys.append(keyboard.Key.shift)
                elif key == 'cmd' or key == 'super':
                    keys.append(keyboard.Key.cmd)
                elif len(key) == 1:
                    keys.append(key)
                else:
                    try:
                        keys.append(getattr(keyboard.Key, key))
                    except AttributeError:
                        logger.warning(f"Unknown key: {key}")
            
            combinations[action] = frozenset(keys)
        
        return combinations
    
    def start(self):
        """Start listening for keyboard events"""
        if self.is_running:
            logger.warning("Keyboard listener already running")
            return
        
        logger.info("Starting keyboard listener")
        
        self.is_running = True
        
        # Start listener in a separate thread
        self.listener_thread = threading.Thread(target=self._start_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()
    
    def stop(self):
        """Stop listening for keyboard events"""
        if not self.is_running:
            logger.warning("Keyboard listener not running")
            return
        
        logger.info("Stopping keyboard listener")
        
        self.is_running = False
        
        if self.listener:
            self.listener.stop()
    
    def _start_listener(self):
        """Start the keyboard listener"""
        try:
            with keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            ) as listener:
                self.listener = listener
                listener.join()
        except Exception as e:
            logger.error(f"Error in keyboard listener: {e}")
            self.is_running = False
    
    def _on_key_press(self, key):
        """
        Handle key press events.
        
        Args:
            key: The key that was pressed
        """
        if not self.is_running:
            return
        
        try:
            # Convert key to a comparable format
            if hasattr(key, 'char') and key.char:
                comparable_key = key.char.lower()
            else:
                comparable_key = key
            
            # Add key to current keys
            self.current_keys.add(comparable_key)
            
            # Check if any hotkey combination is pressed
            self._check_hotkeys()
        
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _on_key_release(self, key):
        """
        Handle key release events.
        
        Args:
            key: The key that was released
        """
        if not self.is_running:
            return
        
        try:
            # Convert key to a comparable format
            if hasattr(key, 'char') and key.char:
                comparable_key = key.char.lower()
            else:
                comparable_key = key
            
            # Remove key from current keys
            self.current_keys.discard(comparable_key)
        
        except Exception as e:
            logger.error(f"Error handling key release: {e}")
    
    def _check_hotkeys(self):
        """Check if any hotkey combination is pressed"""
        current_set = frozenset(self.current_keys)
        
        for action, combination in self.hotkey_combinations.items():
            if combination.issubset(current_set):
                logger.info(f"Hotkey triggered: {action}")
                
                # Emit the corresponding signal
                if action == "start_stop_recording":
                    self.start_stop_recording_triggered.emit()
                elif action == "transcribe_file":
                    self.transcribe_file_triggered.emit()
                elif action == "settings":
                    self.settings_triggered.emit()
                elif action == "quit":
                    self.quit_triggered.emit()
    
    def update_hotkeys(self, hotkeys):
        """
        Update the hotkeys.
        
        Args:
            hotkeys (dict): Dictionary mapping actions to keyboard shortcuts
        """
        self.hotkeys = hotkeys
        self.hotkey_combinations = self._parse_hotkeys(hotkeys)
