"""
Transient Absorption Analyser main entry point.
"""
import sys
from PySide6.QtWidgets import QApplication
from transient_absorption_analyser.src.ui.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style and info
    app.setApplicationName("Transient Absorption Analyzer")
    app.setStyle("Fusion")  # Modern looking style
    
    # Create and show main window
    window = MainWindow()
    window.show()  # Show first to initialize proper geometry
    window.showMaximized()  # Then maximize
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 