#!/usr/bin/env python3
"""
Simple test script to check if system tray icons work on this system
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction

def main():
    app = QApplication(sys.argv)
    
    # Check if system tray is supported
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("ERROR: System tray is not available on this system")
        return 1
    
    # Create tray icon
    tray_icon = QSystemTrayIcon()
    
    # Try to use a standard icon first
    from PyQt6.QtWidgets import QStyle
    style = app.style()
    icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
    tray_icon.setIcon(icon)
    print(f"Using standard icon: {icon.isNull()=}")
    
    # Try to use our custom icon if it exists
    icon_path = os.path.join(os.path.dirname(__file__), "resources/icon.png")
    if os.path.exists(icon_path):
        print(f"Found custom icon at: {icon_path}")
        custom_icon = QIcon(icon_path)
        tray_icon.setIcon(custom_icon)
        print(f"Using custom icon: {custom_icon.isNull()=}")
    else:
        print(f"Custom icon not found at: {icon_path}")
    
    # Create a menu
    menu = QMenu()
    action = QAction("Test Action", None)
    action.triggered.connect(lambda: print("Action triggered"))
    menu.addAction(action)
    
    quit_action = QAction("Quit", None)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    
    # Show the tray icon
    tray_icon.show()
    print("Tray icon should be visible now")
    
    # Show a notification
    tray_icon.showMessage(
        "Test Notification",
        "This is a test notification from the tray icon",
        QSystemTrayIcon.MessageIcon.Information,
        3000
    )
    print("Notification should be visible now")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
