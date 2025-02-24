"""
Load tab implementation for data loading and initial processing.
"""
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QTableView
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

import pandas as pd
import numpy as np
from transient_absorption_analyser.src.core.data_processor import DataProcessor, ProcessedData

class LoadTab(QWidget):
    """Tab for loading and processing data files."""
    
    # Signals
    data_processed = Signal(object)  # Emits ProcessedData object
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.data_processor = DataProcessor()
        self.current_data: Optional[ProcessedData] = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # File selection section
        file_section = QWidget()
        file_layout = QVBoxLayout(file_section)
        
        # Signal file selection
        signal_layout = QHBoxLayout()
        signal_label = QLabel("Upload signal file:")
        self.signal_button = QPushButton("Open file dialog")
        self.signal_path_label = QLabel("No file selected")
        signal_layout.addWidget(signal_label)
        signal_layout.addWidget(self.signal_button)
        signal_layout.addWidget(self.signal_path_label)
        file_layout.addLayout(signal_layout)
        
        # Reference file selection
        reference_layout = QHBoxLayout()
        reference_label = QLabel("Upload dark file:")
        self.reference_button = QPushButton("Open file dialog")
        self.reference_path_label = QLabel("No file selected")
        reference_layout.addWidget(reference_label)
        reference_layout.addWidget(self.reference_button)
        reference_layout.addWidget(self.reference_path_label)
        file_layout.addLayout(reference_layout)
        
        # File format info
        format_label = QLabel(
            "File format: excel table typical files (csv, xls, xlsx, txt)"
        )
        file_layout.addWidget(format_label)
        
        # Moving average settings
        ma_section = QWidget()
        ma_layout = QHBoxLayout(ma_section)
        ma_label = QLabel("N = ")
        self.ma_spinbox = QSpinBox()
        self.ma_spinbox.setMinimum(1)
        self.ma_spinbox.setValue(5)
        ma_info = QLabel("Must be integer. Default = 5")
        ma_layout.addWidget(ma_label)
        ma_layout.addWidget(self.ma_spinbox)
        ma_layout.addWidget(ma_info)
        ma_layout.addStretch()
        
        # Load and Go button
        self.process_button = QPushButton("Load and Go")
        self.process_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #673ab7;"
            "   color: white;"
            "   padding: 10px;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #5e35b1;"
            "}"
        )
        
        # Data display tabs
        self.data_tabs = QTabWidget()
        
        # Create tables for different data views
        self.signal_table = QTableView()
        self.dark_table = QTableView()
        self.signal_common_table = QTableView()
        self.dark_common_table = QTableView()
        self.difference_table = QTableView()
        self.ma_table = QTableView()  # New MA table
        
        # Configure tables
        for table in [self.signal_table, self.dark_table, 
                     self.signal_common_table, self.dark_common_table,
                     self.difference_table, self.ma_table]:  # Added MA table to configuration
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableView.SelectRows)
            table.setSelectionMode(QTableView.SingleSelection)
            table.setSortingEnabled(True)
        
        # Add tables to tab widget
        self.data_tabs.addTab(self.signal_table, "signal")
        self.data_tabs.addTab(self.dark_table, "dark")
        self.data_tabs.addTab(self.signal_common_table, "Signal_common")
        self.data_tabs.addTab(self.dark_common_table, "Dark common")
        self.data_tabs.addTab(self.difference_table, "Sig-dark common")
        self.data_tabs.addTab(self.ma_table, "MA")  # Add MA tab
        
        # Add all sections to main layout
        layout.addWidget(file_section)
        layout.addWidget(ma_section)
        layout.addWidget(self.process_button)
        layout.addWidget(self.data_tabs)
        
    def _create_table_model(self, data: pd.DataFrame) -> QStandardItemModel:
        """Create a table model from a pandas DataFrame."""
        model = QStandardItemModel()
        
        # Set headers
        model.setHorizontalHeaderLabels(data.columns)
        
        # Add data
        for row in range(len(data)):
            items = []
            for col in range(len(data.columns)):
                val = data.iloc[row, col]
                # Format numbers with reasonable precision
                if isinstance(val, (float, np.floating)):
                    item = QStandardItem(f"{val:.6f}")
                else:
                    item = QStandardItem(str(val))
                items.append(item)
            model.appendRow(items)
            
        return model
        
    def setup_connections(self):
        """Setup signal connections."""
        # Button connections
        self.signal_button.clicked.connect(
            lambda: self.select_file('signal')
        )
        self.reference_button.clicked.connect(
            lambda: self.select_file('reference')
        )
        self.process_button.clicked.connect(self.process_data)
        
        # Data processor connections
        self.data_processor.processing_complete.connect(
            self.on_processing_complete
        )
        self.data_processor.processing_error.connect(
            self.on_processing_error
        )
        
    @Slot()
    def select_file(self, file_type: str):
        """Handle file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {file_type} file",
            "",
            "Data files (*.csv *.xls *.xlsx *.txt)"
        )
        
        if file_path:
            if file_type == 'signal':
                self.signal_path_label.setText(file_path)
            else:
                self.reference_path_label.setText(file_path)
                
    @Slot()
    def process_data(self):
        """Handle data processing."""
        signal_path = self.signal_path_label.text()
        if signal_path == "No file selected":
            QMessageBox.warning(
                self,
                "Input Error",
                "Please select a signal file."
            )
            return
            
        reference_path = self.reference_path_label.text()
        if reference_path == "No file selected":
            reference_path = None
            QMessageBox.information(
                self,
                "No Reference",
                "No reference file selected. Proceeding with signal data only."
            )
            
        window_size = self.ma_spinbox.value()
        
        # Process data
        self.current_data = self.data_processor.process_files(
            signal_path,
            reference_path,
            window_size
        )
        
    @Slot(ProcessedData)
    def on_processing_complete(self, data: ProcessedData):
        """Handle completed data processing."""
        self.current_data = data
        self.update_data_displays()
        self.data_processed.emit(data)
        
        # Show summary
        QMessageBox.information(
            self,
            "Processing Complete",
            data.get_summary()
        )
        
    @Slot(str)
    def on_processing_error(self, error_msg: str):
        """Handle processing errors."""
        QMessageBox.critical(
            self,
            "Data Processing Error",
            "An error occurred while processing the data:\n\n"
            f"{error_msg}\n\n"
            "Please check your data file format and try again.\n"
            "The expected format is:\n"
            "- First column: Time points\n"
            "- Additional columns: Wavelength measurements (e.g., 532.0, 533.0, etc.)\n"
            "- Supported file types: .csv, .xlsx, .xls, .txt"
        )
        
    def update_data_displays(self):
        """Update data displays with current data."""
        if self.current_data is None:
            return
            
        # Update signal table
        if self.current_data.signal_data is not None:
            model = self._create_table_model(self.current_data.signal_data)
            self.signal_table.setModel(model)
            
        # Update reference table
        if self.current_data.reference_data is not None:
            model = self._create_table_model(self.current_data.reference_data)
            self.dark_table.setModel(model)
            
        # Update common data tables
        if self.current_data.common_data is not None:
            # Signal common
            if hasattr(self.current_data, 'signal_common') and self.current_data.signal_common is not None:
                model = self._create_table_model(self.current_data.signal_common)
                self.signal_common_table.setModel(model)
                
            # Dark common
            if hasattr(self.current_data, 'dark_common') and self.current_data.dark_common is not None:
                model = self._create_table_model(self.current_data.dark_common)
                self.dark_common_table.setModel(model)
                
            # Difference (raw signal - dark)
            model = self._create_table_model(self.current_data.common_data)
            self.difference_table.setModel(model)
            
            # MA (Moving Average) table - shows the processed data after moving average
            model = self._create_table_model(self.current_data.moving_average_data)  # Now using the separate MA data
            self.ma_table.setModel(model)
            
        # Resize columns to content
        for table in [self.signal_table, self.dark_table, 
                     self.signal_common_table, self.dark_common_table,
                     self.difference_table, self.ma_table]:
            if table.model() is not None:
                table.resizeColumnsToContents()
                table.resizeRowsToContents()

    def get_current_data(self) -> Optional[ProcessedData]:
        """Get current processed data."""
        return self.current_data
        
    def get_moving_average_window(self) -> int:
        """Get current moving average window size."""
        return self.ma_spinbox.value() 