"""
Main window implementation for the Transient Absorption Analyser.
"""
from PySide6.QtWidgets import (
    QMainWindow, 
    QTabWidget,
    QVBoxLayout, 
    QWidget, 
    QPushButton,
    QMessageBox,
    QFileDialog,
    QHBoxLayout
)
from PySide6.QtCore import Qt, Slot

from .tabs.load_tab import LoadTab
from .tabs.spectrum_tab import SpectrumTab
from .tabs.intensity_tab import IntensityTab
from transient_absorption_analyser.src.core.export_manager import ExportManager

class MainWindow(QMainWindow):
    """Main window of the application."""
    
    def __init__(self):
        super().__init__()
        self.export_manager = ExportManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Transient Absorption Analyzer")
        self.resize(1200, 800)  # Set default size
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)  # Add some padding
        
        # Create top section with export button
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create export button
        self.export_button = QPushButton("Export")
        self.export_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #4CAF50;"
            "   color: white;"
            "   padding: 8px 16px;"  # Increased horizontal padding
            "   border-radius: 4px;"
            "   min-width: 80px;"  # Set minimum width
            "}"
            "QPushButton:hover {"
            "   background-color: #45a049;"
            "}"
        )
        self.export_button.clicked.connect(self.handle_export)
        
        # Add stretch to push button to the right
        top_layout.addStretch(1)
        top_layout.addWidget(self.export_button)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.load_tab = LoadTab()
        self.spectrum_tab = SpectrumTab()
        self.intensity_tab = IntensityTab()
        
        # Add tabs
        self.tabs.addTab(self.load_tab, "Load")
        self.tabs.addTab(self.spectrum_tab, "Spectrum")
        self.tabs.addTab(self.intensity_tab, "Intensity")
        
        # Add widgets to layout
        layout.addWidget(top_section)
        layout.addWidget(self.tabs)
        
        # Connect signals between tabs
        self.load_tab.data_processed.connect(self.on_data_processed)
        
    @Slot(object)
    def on_data_processed(self, processed_data):
        """Handle processed data from Load tab."""
        self.spectrum_tab.update_data(processed_data)
        self.intensity_tab.update_data(processed_data)
        
    @Slot()
    def handle_export(self):
        """Handle export button click."""
        try:
            # Get export directory from user
            export_path = QFileDialog.getExistingDirectory(
                self, "Select Export Directory"
            )
            if not export_path:
                return
                
            # Get current data
            data = self.load_tab.get_current_data()
            if data is None:
                QMessageBox.warning(
                    self,
                    "Export Error",
                    "No data available for export. Please load and process data first."
                )
                return
                
            # Export data and plots
            export_dir = self.export_manager.export_all(
                export_path,
                data,  # Pass ProcessedData object directly
                self.get_current_plots(),
                self.load_tab.get_moving_average_window()
            )
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Complete",
                f"Data and figures exported to:\n{export_dir}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Error during export: {str(e)}"
            )
            
    def get_current_plots(self):
        """Get current plot objects from tabs."""
        return {
            'plot_A': self.spectrum_tab.plot_a,
            'plot_B': self.spectrum_tab.plot_b,
            'plot_C': self.intensity_tab.plot_c
        } 