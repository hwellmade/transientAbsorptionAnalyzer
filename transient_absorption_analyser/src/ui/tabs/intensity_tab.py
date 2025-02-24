"""
Intensity tab implementation for average intensity plotting.
"""
from typing import Optional, Dict, List, Tuple
import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QFrame,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit
)
from PySide6.QtCore import Qt, Slot
from matplotlib.widgets import RectangleSelector, SpanSelector

from ..plot_widget import PlotWidget
from transient_absorption_analyser.src.core.data_processor import ProcessedData

class IntensityTab(QWidget):
    """Tab for intensity visualization."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_data: Optional[ProcessedData] = None
        self.selector = None
        self.setup_ui()
        self._initialize_default_view()
        
    def setup_ui(self):
        """Set up the UI layout."""
        main_layout = QHBoxLayout()  # Main layout is horizontal for left-right split
        main_layout.setContentsMargins(20, 0, 0, 0)  # Add 20px padding on the left
        main_layout.setSpacing(10)  # Spacing between panels

        # Left Panel (Time series plot)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)  # Add small spacing
        left_panel.setContentsMargins(20, 5, 5, 5)  # Add more padding on the left

        # Title for left panel
        left_title = QLabel("Set the time range")
        left_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        left_title.setContentsMargins(0, 0, 0, 5)  # Add bottom padding to title
        left_panel.addWidget(left_title)

        # Plot container for left plot
        plot_container_left = QWidget()
        plot_layout_left = QVBoxLayout(plot_container_left)
        plot_layout_left.setContentsMargins(20, 0, 0, 0)  # Add more padding on the left
        plot_layout_left.setSpacing(0)

        # Plot A (Time series) with its toolbar
        self.plot_a = PlotWidget()
        self.plot_a.setFixedSize(480, 500)  # Set both width and height explicitly
        plot_layout_left.addWidget(self.plot_a)

        # Add tag input section
        tag_layout = QHBoxLayout()
        tag_layout.setContentsMargins(5, 5, 5, 5)  # Add small padding
        tag_label = QLabel("Tag:")
        self.tag_input = QLineEdit()
        self.apply_tag_button = QPushButton("Apply")
        self.apply_tag_button.clicked.connect(self._on_apply_tag)
        
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(self.tag_input)
        tag_layout.addWidget(self.apply_tag_button)
        plot_layout_left.addLayout(tag_layout)
        
        left_panel.addWidget(plot_container_left)
        left_panel.addStretch(1)  # Push everything to the top
        
        # Add the left panel to main layout
        left_container = QWidget()
        left_container.setLayout(left_panel)
        main_layout.addWidget(left_container)

        # Right Panel (Average intensity plot)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(5)  # Add small spacing
        right_panel.setContentsMargins(5, 5, 5, 5)  # Keep standard padding

        # Title for right panel
        right_title = QLabel("average intensity v.s. wavelength")
        right_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        right_title.setContentsMargins(0, 0, 0, 5)  # Add bottom padding to title
        right_panel.addWidget(right_title)

        # Plot container for right plot
        plot_container_right = QWidget()
        plot_layout_right = QVBoxLayout(plot_container_right)
        plot_layout_right.setContentsMargins(0, 0, 0, 0)
        plot_layout_right.setSpacing(0)

        # Plot C (Average intensity vs wavelength) with its toolbar
        self.plot_c = PlotWidget()
        self.plot_c.setFixedSize(480, 500)  # Set both width and height explicitly
        plot_layout_right.addWidget(self.plot_c)
        
        right_panel.addWidget(plot_container_right)
        right_panel.addStretch(1)  # Push everything to the top
        
        # Add the right panel to main layout
        right_container = QWidget()
        right_container.setLayout(right_panel)
        main_layout.addWidget(right_container)

        # Set the main layout
        self.setLayout(main_layout)
        
    def _initialize_default_view(self):
        """Initialize plot views with default ranges."""
        # Set default ranges and labels for Plot A
        self.plot_a.ax.set_xlim(0, 1)
        self.plot_a.ax.set_ylim(-1, 1)
        self.plot_a.ax.set_xlabel("Time (ns)", fontsize=10, labelpad=5)
        self.plot_a.ax.set_ylabel("Intensity (a.u.)", fontsize=10, labelpad=5)
        self.plot_a.ax.set_title("absorption", pad=10, fontsize=12)  # Add default title
        self.plot_a.canvas.draw()
        
        # Set default ranges for Plot C (average intensity plot)
        self.plot_c.ax.set_xlim(0, 1)
        self.plot_c.ax.set_ylim(-1, 1)
        self.plot_c.canvas.draw()
        
    def _update_plot_scales(self, data: ProcessedData):
        """Update plot scales based on actual data ranges."""
        try:
            # Get time range from the data
            time_points = data.time_points
            x_min, x_max = min(time_points), max(time_points)
            x_padding = (x_max - x_min) * 0.05  # 5% padding
            
            # Get value range from the processed data
            all_values = []
            for col in data.common_data.columns[1:]:  # Skip time column
                values = data.common_data[col].values
                all_values.extend(values)
                
            if all_values:
                # Calculate robust y-range using percentiles
                y_values = np.array(all_values)
                y_min, y_max = np.percentile(y_values, [1, 99])
                y_padding = (y_max - y_min) * 0.1  # 10% padding
                
                # Update Plot A with the new ranges
                self.plot_a.ax.set_xlim(x_min - x_padding, x_max + x_padding)
                self.plot_a.ax.set_ylim(y_min - y_padding, y_max + y_padding)
                self.plot_a.canvas.draw()
                
                print(f"Updated plot scales - X: [{x_min - x_padding:.2f}, {x_max + x_padding:.2f}], "
                      f"Y: [{y_min - y_padding:.6f}, {y_max + y_padding:.6f}]")
        except Exception as e:
            print(f"Error updating plot scales: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def _setup_selector(self):
        """Setup the time range selector on Plot A."""
        if self.selector is not None:
            self.selector.disconnect_events()
            
        self.selector = SpanSelector(
            self.plot_a.ax,
            self._on_select,
            'horizontal',
            useblit=True,
            props=dict(alpha=0.3, facecolor='tab:blue'),
            interactive=True,
            drag_from_anywhere=True
        )
        
        # Add instruction text
        self.plot_a.ax.text(
            0.98, 0.02,
            'Drag to select time period',
            transform=self.plot_a.ax.transAxes,
            ha='right',
            va='bottom',
            color='red',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
        
    def _on_select(self, xmin: float, xmax: float):
        """Handle time range selection."""
        if self.current_data is None:
            return
            
        try:
            # Calculate average intensity for the selected time range using MA data
            time_mask = (self.current_data.time_points >= xmin) & (self.current_data.time_points <= xmax)
            
            if not any(time_mask):
                print("No data points in selected range")
                return
                
            wavelengths = []
            averages = []
            
            for col in self.current_data.moving_average_data.columns[1:]:  # Use MA data
                try:
                    wave = float(col)
                    values = self.current_data.moving_average_data[col].values[time_mask]  # Use MA data
                    avg = np.mean(values)
                    if not np.isnan(avg):
                        wavelengths.append(wave)
                        averages.append(avg)
                except (ValueError, KeyError) as e:
                    print(f"Error processing column {col}: {str(e)}")
                    continue
                    
            if wavelengths and averages:
                # Sort by wavelength
                wavelengths = np.array(wavelengths)
                averages = np.array(averages)
                sort_idx = np.argsort(wavelengths)
                wavelengths = wavelengths[sort_idx]
                averages = averages[sort_idx]
                
                # Update plot only
                self.plot_c.plot_average_intensity(
                    wavelengths.tolist(),
                    averages.tolist(),
                    (xmin, xmax)
                )
            else:
                print("No valid data for average intensity calculation")
                
        except Exception as e:
            print(f"Error calculating average intensity: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def _on_apply_tag(self):
        """Handle apply tag button click."""
        tag = self.tag_input.text().strip()
        if tag:
            # Update title for Plot A
            self.plot_a.ax.set_title(f"absorption: {tag}", pad=10, fontsize=12)
            self.plot_a.canvas.draw()

    def update_data(self, data: ProcessedData):
        """Update the displayed data."""
        if data is None:
            return
            
        self.current_data = data  # Store the data for later use
            
        try:
            # Update Plot A preview with all wavelengths using MA data
            wavelength_columns = [col for col in data.moving_average_data.columns[1:]]  # Use MA data
            plot_data = {}
            
            for col in wavelength_columns:
                try:
                    wave = float(col)
                    values = data.moving_average_data[col].values  # Use MA data
                    if len(values) > 0 and not np.all(np.isnan(values)):
                        plot_data[wave] = values
                        print(f"Added wavelength {wave}nm with {len(values)} points")
                        print(f"Value range: {min(values)} to {max(values)}")
                except (ValueError, KeyError) as e:
                    print(f"Error processing column {col}: {str(e)}")
                    continue
            
            if plot_data:
                print(f"Plotting {len(plot_data)} wavelengths")
                print(f"Time points range: {min(data.time_points)} to {max(data.time_points)}")
                
                # Update Plot A with all wavelengths
                self.plot_a.plot_all_wavelengths(
                    data.time_points,
                    plot_data
                )
                
                # Restore or set default title for Plot A
                current_title = self.plot_a.ax.get_title()
                if not current_title or current_title == "":
                    self.plot_a.ax.set_title("absorption", pad=10, fontsize=12)
                self.plot_a.canvas.draw()
                
                # Initialize Plot C with empty view
                self.plot_c.clear()
                self.plot_c.ax.set_xlabel("Wavelength (nm)")
                self.plot_c.ax.set_ylabel("Average Intensity")
                self.plot_c.ax.set_title("Select time range in Plot A to calculate average")
                self.plot_c.ax.grid(True)
                self.plot_c.canvas.draw()
                
                # Setup the selector for time range selection
                self._setup_selector()
            else:
                print("No valid wavelength data available for plotting")
                for plot in [self.plot_a, self.plot_c]:
                    plot.clear()
                    plot.ax.text(
                        0.5, 0.5,
                        "No valid wavelength data available",
                        ha='center', va='center'
                    )
                    plot.canvas.draw()
                    
        except Exception as e:
            print(f"Error updating intensity plots: {str(e)}")
            import traceback
            traceback.print_exc()
            for plot in [self.plot_a, self.plot_c]:
                plot.clear()
                plot.canvas.draw()
                
    @Slot()
    def calculate_average(self):
        """Calculate and plot average intensities."""
        if self.current_data is None or self.selector is None:
            return
            
        try:
            # Get time range indices
            time_points = np.array(self.current_data.time_points)
            xmin, xmax = self.selector.extents
            
            # Get wavelength columns (excluding time column) from MA data
            wavelength_columns = [col for col in self.current_data.moving_average_data.columns[1:]]  # Use MA data
            
            # Calculate averages using MA data
            wavelengths = []
            averages = []
            
            for col in wavelength_columns:
                try:
                    wave = float(col)
                    values = self.current_data.moving_average_data[col].values  # Use MA data
                    avg = np.mean(values[(time_points >= xmin) & (time_points <= xmax)])
                    wavelengths.append(wave)
                    averages.append(avg)
                except (ValueError, KeyError):
                    continue
                    
            # Sort by wavelength
            wavelengths = np.array(wavelengths)
            averages = np.array(averages)
            sort_idx = np.argsort(wavelengths)
            wavelengths = wavelengths[sort_idx]
            averages = averages[sort_idx]
            
            # Plot results if we have data
            if len(wavelengths) > 0:
                self.plot_c.plot_average_intensity(
                    wavelengths.tolist(),
                    averages.tolist(),
                    (xmin, xmax)
                )
            else:
                self.plot_c.clear()
                self.plot_c.ax.text(
                    0.5, 0.5,
                    "No valid wavelength data available",
                    ha='center', va='center'
                )
                
        except Exception as e:
            print(f"Error calculating averages: {str(e)}")
            self.plot_c.clear() 