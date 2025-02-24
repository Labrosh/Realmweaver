#!/usr/bin/env python3

# Realmweaver - A Procedural World Generation Tool
# This is our main entry point that launches the UI application.
# The world generation logic lives in world_generator.py
# The visualization logic lives in visualization.py
# The UI implementation lives in main_window.py

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    # Force platform plugin if needed
    import os
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
