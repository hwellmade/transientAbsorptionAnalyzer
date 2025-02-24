"""
Spectrum tab implementation for wavelength plotting.
"""
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QScrollArea,
    QFrame,
    QCheckBox,
    QToolBox,
    QSizePolicy,
    QLineEdit
)
from PySide6.QtCore import Qt, Slot, QSize
import numpy as np

from ..plot_widget import PlotWidget
from transient_absorption_analyser.src.core.data_processor import ProcessedData

class SpectrumTab(QWidget):
    """Tab for spectrum visualization."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_data: Optional[ProcessedData] = None
        self.wavelength_buttons = []  # Initialize the list
        self.setup_ui()
        self._initialize_default_view()
        
    def setup_ui(self):
        """Set up the UI layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 0, 0, 0)  # Add 20px padding on the left
        main_layout.setSpacing(0)  # Remove spacing between elements
        
        # Create top section for plots
        plots_layout = QHBoxLayout()
        plots_layout.setContentsMargins(20, 0, 0, 0)  # Add 20px padding on the left
        plots_layout.setSpacing(10)  # Add small spacing between plots
        
        # Left side - Plot A and controls
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 5, 5, 5)  # Add more padding on the left
        left_layout.setSpacing(5)  # Add small spacing
        
        # Add padding widget for toolbar
        toolbar_padding = QWidget()
        toolbar_padding.setFixedHeight(40)  # Padding for toolbar
        left_layout.addWidget(toolbar_padding)
        
        # Plot A with increased height but reduced width
        self.plot_a = PlotWidget()
        self.plot_a.setFixedSize(480, 500)  # Set both width and height explicitly
        left_layout.addWidget(self.plot_a)
        
        # Tag input section
        tag_layout = QHBoxLayout()
        tag_layout.setContentsMargins(5, 5, 5, 5)  # Add small padding
        tag_label = QLabel("Tag:")
        self.tag_input = QLineEdit()
        self.apply_tag_button = QPushButton("Apply")
        self.apply_tag_button.clicked.connect(self._on_apply_tag)
        
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(self.tag_input)
        tag_layout.addWidget(self.apply_tag_button)
        left_layout.addLayout(tag_layout)
        
        # Add stretch at the bottom of left layout to push everything up
        left_layout.addStretch()
        
        # Create left container
        left_container = QWidget()
        left_container.setLayout(left_layout)
        plots_layout.addWidget(left_container)
        
        # Right side - Plot B and wavelength selection
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)  # Keep standard padding
        right_layout.setSpacing(5)  # Add small spacing
        
        # Add padding widget for toolbar
        toolbar_padding_right = QWidget()
        toolbar_padding_right.setFixedHeight(40)  # Padding for toolbar
        right_layout.addWidget(toolbar_padding_right)
        
        # Plot B with increased height but reduced width
        self.plot_b = PlotWidget()
        self.plot_b.setFixedSize(480, 500)  # Set both width and height explicitly
        right_layout.addWidget(self.plot_b)
        
        # Create wavelength selection area
        wavelength_group = QFrame()
        wavelength_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        wavelength_layout = QVBoxLayout(wavelength_group)
        wavelength_layout.setContentsMargins(5, 5, 5, 5)  # Add small padding
        
        # Add header with label
        header_layout = QHBoxLayout()
        header_label = QLabel("Select Wavelengths:")
        header_layout.addWidget(header_label)
        wavelength_layout.addLayout(header_layout)
        
        # Create scrollable area for wavelength selection
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(150)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        wavelength_widget = QWidget()
        self.wavelength_layout = QVBoxLayout(wavelength_widget)
        self.wavelength_layout.setSpacing(2)
        self.wavelength_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(wavelength_widget)
        wavelength_layout.addWidget(scroll_area)
        
        # Add wavelength selection to right layout
        right_layout.addWidget(wavelength_group)
        
        # Add stretch at the bottom of right layout to push everything up
        right_layout.addStretch()
        
        # Create right container
        right_container = QWidget()
        right_container.setLayout(right_layout)
        plots_layout.addWidget(right_container)
        
        # Add plots section to main layout
        main_layout.addLayout(plots_layout)
        
        self.setLayout(main_layout)
        
    def _initialize_default_view(self):
        """Initialize plot views with default ranges."""
        # Start with a basic view that will be updated when data arrives
        for plot in [self.plot_a, self.plot_b]:
            plot.ax.set_xlim(0, 1)
            plot.ax.set_ylim(-1, 1)
            plot.ax.set_xlabel("Time (ns)", fontsize=10, labelpad=5)
            plot.ax.set_ylabel("Intensity (a.u.)", fontsize=10, labelpad=5)
            plot.ax.set_title("absorption", pad=10, fontsize=12)  # Add default title
            plot.canvas.draw()
        
    def _update_plot_scales(self, data: ProcessedData):
        """Update plot scales based on actual data ranges."""
        try:
            # Get time range from the data
            time_points = data.time_points
            x_min, x_max = min(time_points), max(time_points)
            x_padding = (x_max - x_min) * 0.05  # 5% padding
            
            # Get value range from the processed data (moving_average_data contains smoothed signal-reference)
            all_values = []
            for col in data.moving_average_data.columns[1:]:  # Skip time column
                values = data.moving_average_data[col].values
                all_values.extend(values)
                
            if all_values:
                # Calculate robust y-range using percentiles to avoid outliers
                y_values = np.array(all_values)
                y_min, y_max = np.percentile(y_values, [1, 99])  # Use 1st and 99th percentiles
                y_padding = (y_max - y_min) * 0.1  # 10% padding
                
                # Update both plots with the new ranges
                for plot in [self.plot_a, self.plot_b]:
                    plot.ax.set_xlim(x_min - x_padding, x_max + x_padding)
                    plot.ax.set_ylim(y_min - y_padding, y_max + y_padding)
                    plot.canvas.draw()
                    
                print(f"Updated plot scales - X: [{x_min - x_padding:.2f}, {x_max + x_padding:.2f}], "
                      f"Y: [{y_min - y_padding:.6f}, {y_max + y_padding:.6f}]")
        except Exception as e:
            print(f"Error updating plot scales: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def update_data(self, data: ProcessedData):
        """Update displayed data."""
        self.current_data = data
        
        try:
            # First update the plot scales based on the new data
            self._update_plot_scales(data)
            
            # Get wavelength columns (excluding time column)
            wavelength_columns = [col for col in data.moving_average_data.columns[1:]]  # Use MA data
            print(f"Found {len(wavelength_columns)} wavelength columns")
            
            # Create data dictionary for plotting
            plot_data = {}
            for col in wavelength_columns:
                try:
                    wave = float(col)
                    values = data.moving_average_data[col].to_numpy()  # Use MA data
                    # Validate data
                    if len(values) > 0 and not np.all(np.isnan(values)):
                        plot_data[wave] = values
                        print(f"Added wavelength {wave}nm with {len(values)} points")
                        print(f"Value range: {min(values)} to {max(values)}")
                except (ValueError, KeyError) as e:
                    print(f"Error processing column {col}: {str(e)}")
                    continue
            
            # Update Plot A with available wavelengths
            if plot_data:
                print(f"\nPlotting {len(plot_data)} wavelengths")
                print(f"Time points: {len(data.time_points)} points")
                print(f"Time range: {min(data.time_points)} to {max(data.time_points)}")
                
                self.plot_a.plot_all_wavelengths(
                    data.time_points,
                    plot_data
                )
                
                # Restore or set default title for Plot A
                current_title = self.plot_a.ax.get_title()
                if not current_title or current_title == "":
                    self.plot_a.ax.set_title("absorption", pad=10, fontsize=12)
                self.plot_a.canvas.draw()
                
                # Update wavelength selection
                self.update_wavelength_buttons(sorted(plot_data.keys()))
                
                # Show all curves in grey initially in Plot B
                self.plot_b.plot_highlighted_wavelengths(
                    data.time_points,
                    plot_data,
                    []  # No wavelengths highlighted initially
                )
                
                # Restore or set default title for Plot B
                current_title = self.plot_b.ax.get_title()
                if not current_title or current_title == "":
                    self.plot_b.ax.set_title("absorption", pad=10, fontsize=12)
                self.plot_b.canvas.draw()
            else:
                print("No valid wavelength data available for plotting")
                self.plot_a.clear()
                self.plot_b.clear()
                for plot in [self.plot_a, self.plot_b]:
                    plot.ax.text(
                        0.5, 0.5,
                        "No valid wavelength data available",
                        ha='center', va='center'
                    )
            
        except Exception as e:
            print(f"Error updating spectrum plots: {str(e)}")
            import traceback
            traceback.print_exc()
            self.plot_a.clear()
            self.plot_b.clear()
            
    def update_wavelength_buttons(self, wavelengths: list):
        """Update wavelength selection checkboxes."""
        # Clear existing buttons
        while self.wavelength_layout.count():
            item = self.wavelength_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.wavelength_buttons.clear()
        
        # Add new checkboxes
        for wavelength in sorted(wavelengths):
            checkbox = QCheckBox(f"{wavelength:.1f} nm")
            checkbox.setProperty('wavelength', wavelength)
            checkbox.stateChanged.connect(self.on_wavelength_selection_changed)
            self.wavelength_buttons.append(checkbox)
            self.wavelength_layout.addWidget(checkbox)
            
        # Add stretch at the end
        self.wavelength_layout.addStretch()

    def on_wavelength_selection_changed(self):
        """Handle wavelength selection changes."""
        if self.current_data is None:
            return
            
        try:
            # Get all selected wavelengths
            selected_wavelengths = []
            for button in self.wavelength_buttons:
                if button.isChecked():
                    selected_wavelengths.append(button.property('wavelength'))
            
            # Get wavelength columns (excluding time column)
            wavelength_columns = [col for col in self.current_data.moving_average_data.columns[1:]]  # Use MA data
            
            # Create data dictionary for plotting
            plot_data = {}
            for col in wavelength_columns:
                try:
                    wave = float(col)
                    plot_data[wave] = self.current_data.moving_average_data[col].values  # Use MA data
                except (ValueError, KeyError):
                    continue
            
            # Update Plot B
            if plot_data:
                self.plot_b.plot_highlighted_wavelengths(
                    self.current_data.time_points,
                    plot_data,
                    selected_wavelengths
                )
                
                # Sync zoom if enabled
                if self.plot_a.is_sync_enabled():
                    xlim, ylim = self.plot_a.get_current_view()
                    self.plot_b.set_view(xlim, ylim)
            else:
                self.plot_b.clear()
                self.plot_b.ax.text(
                    0.5, 0.5,
                    "No valid wavelength data available",
                    ha='center', va='center'
                )
                
        except Exception as e:
            print(f"Error updating highlighted wavelength plot: {str(e)}")
            self.plot_b.clear()

    @Slot()
    def save_current_view(self):
        """Save current plot view."""
        # This will be connected to the export manager
        pass 

    def _on_plot_a_draw(self, event):
        """Handle plot A draw event with debouncing."""
        if not self._sync_in_progress and self.plot_a.is_sync_enabled():
            self._sync_in_progress = True
            try:
                xlim, ylim = self.plot_a.get_current_view()
                self.plot_b.set_view(xlim, ylim)
            finally:
                self._sync_in_progress = False
                
    def _on_plot_b_draw(self, event):
        """Handle plot B draw event with debouncing."""
        if not self._sync_in_progress and self.plot_a.is_sync_enabled():
            self._sync_in_progress = True
            try:
                xlim, ylim = self.plot_b.get_current_view()
                self.plot_a.set_view(xlim, ylim)
            finally:
                self._sync_in_progress = False
                
    def _on_apply_tag(self):
        """Handle apply tag button click."""
        tag = self.tag_input.text().strip()
        if tag:
            # Update titles for both plots
            self.plot_a.ax.set_title(f"absorption: {tag}", pad=10, fontsize=12)
            self.plot_b.ax.set_title(f"absorption: {tag}", pad=10, fontsize=12)
            # Redraw both canvases
            self.plot_a.canvas.draw()
            self.plot_b.canvas.draw() 