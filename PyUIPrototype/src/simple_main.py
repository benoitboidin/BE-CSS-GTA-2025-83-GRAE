"""
Simplified main entry point for the PyUI Accelerator Visualization Prototype
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from ui.simple_main_window import SimpleMainWindow


def main():
    """Main application function"""
    # Create the application
    app = QApplication(sys.argv)
    
    # Apply stylesheet if available
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'resources', 'styles.qss'), 'r') as f:
            app.setStyleSheet(f.read())
    except:
        print("Could not load stylesheet")
    
    # Create and show the main window
    window = SimpleMainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
