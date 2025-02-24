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
    QLineEdit,
    QMessageBox
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
        self._sync_in_progress = False  # Add sync flag
        
        # Create plots first
        self.plot_a = PlotWidget()
        self.plot_c = PlotWidget()
        
        # Connect plot draw events for sync zoom
        self.plot_a.canvas.mpl_connect('draw_event', self._on_plot_a_draw)
        self.plot_c.canvas.mpl_connect('draw_event', self._on_plot_c_draw)
        
        self.setup_ui()
        self._initialize_default_view()
        
    def setup_ui(self):
        """Set up the UI layout."""
        # Main layout is horizontal for left-right split
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove outer margins
        main_layout.setSpacing(20)  # Keep spacing between panels

        # Left Panel (Time series plot)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)
        left_panel.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Title for left panel
        left_title = QLabel("Set the time range")
        left_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        left_title.setContentsMargins(5, 5, 5, 5)  # Add small padding to title
        left_title.setAlignment(Qt.AlignCenter)  # Center align the text
        left_panel.addWidget(left_title)

        # Plot container for left plot
        plot_container_left = QWidget()
        plot_layout_left = QVBoxLayout(plot_container_left)
        plot_layout_left.setContentsMargins(0, 0, 0, 0)  # Remove margins
        plot_layout_left.setSpacing(5)

        # Plot A (Time series) with its toolbar
        self.plot_a = PlotWidget()
        self.plot_a.setFixedSize(600, 400)  # Use fixed size like spectrum tab
        plot_layout_left.addWidget(self.plot_a)

        # Add tag input section
        tag_layout = QHBoxLayout()
        tag_layout.setContentsMargins(5, 5, 5, 5)
        tag_label = QLabel("Tag:")
        self.tag_input = QLineEdit()
        self.apply_tag_button = QPushButton("Apply")
        self.apply_tag_button.clicked.connect(self._on_apply_tag)
        
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(self.tag_input)
        tag_layout.addWidget(self.apply_tag_button)
        plot_layout_left.addLayout(tag_layout)
        
        # Add time range input section
        time_range_layout = QHBoxLayout()
        time_range_layout.setContentsMargins(5, 5, 5, 5)
        
        # Time min input
        time_min_layout = QHBoxLayout()
        time_min_label = QLabel("time min:")
        self.time_min_input = QLineEdit()
        self.time_min_input.setPlaceholderText("Enter min time")
        time_min_unit = QLabel("(ns)")
        time_min_layout.addWidget(time_min_label)
        time_min_layout.addWidget(self.time_min_input)
        time_min_layout.addWidget(time_min_unit)
        
        # Time max input
        time_max_layout = QHBoxLayout()
        time_max_label = QLabel("time max:")
        self.time_max_input = QLineEdit()
        self.time_max_input.setPlaceholderText("Enter max time")
        time_max_unit = QLabel("(ns)")
        time_max_layout.addWidget(time_max_label)
        time_max_layout.addWidget(self.time_max_input)
        time_max_layout.addWidget(time_max_unit)
        
        # Apply button for time range
        self.apply_time_range_button = QPushButton("Apply Range")
        self.apply_time_range_button.clicked.connect(self._on_apply_time_range)
        
        # Add all to time range layout
        time_range_layout.addLayout(time_min_layout)
        time_range_layout.addLayout(time_max_layout)
        time_range_layout.addWidget(self.apply_time_range_button)
        
        plot_layout_left.addLayout(time_range_layout)
        
        left_panel.addWidget(plot_container_left)
        left_panel.addStretch(1)  # Push everything to the top
        
        # Create left container
        left_container = QWidget()
        left_container.setLayout(left_panel)
        main_layout.addWidget(left_container, 1)  # Equal weight

        # Right Panel (Average intensity plot)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(5)
        right_panel.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Title for right panel
        right_title = QLabel("average intensity v.s. wavelength")
        right_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        right_title.setContentsMargins(5, 5, 5, 5)  # Add small padding to title
        right_title.setAlignment(Qt.AlignCenter)  # Center align the text
        right_panel.addWidget(right_title)

        # Plot container for right plot
        plot_container_right = QWidget()
        plot_layout_right = QVBoxLayout(plot_container_right)
        plot_layout_right.setContentsMargins(0, 0, 0, 0)
        plot_layout_right.setSpacing(5)

        # Plot C (Average intensity vs wavelength) with its toolbar
        self.plot_c = PlotWidget()
        self.plot_c.setFixedSize(600, 400)  # Match spectrum tab dimensions
        plot_layout_right.addWidget(self.plot_c)
        
        right_panel.addWidget(plot_container_right)
        right_panel.addStretch(1)  # Push everything to the top
        
        # Create right container
        right_container = QWidget()
        right_container.setLayout(right_panel)
        main_layout.addWidget(right_container, 1)  # Equal weight

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
            
            for col in self.current_data.moving_average_data.columns[1:]:
                try:
                    wave = float(col)
                    values = self.current_data.moving_average_data[col].values[time_mask]
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
                
                # Let plot_average_intensity handle its own scale calculation
                self.plot_c.plot_average_intensity(
                    wavelengths.tolist(),
                    averages.tolist(),
                    (xmin, xmax),
                    respect_limits=False  # Let it calculate its own limits
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
            # Get wavelength columns (excluding time column)
            wavelength_columns = [col for col in data.moving_average_data.columns[1:]]  # Use MA data
            print(f"[Tab 3] Found {len(wavelength_columns)} wavelength columns")
            
            # Create data dictionary for plotting
            plot_data = {}
            all_values = []  # Track all values for scale calculation
            for col in wavelength_columns:
                try:
                    wave = float(col)
                    values = data.moving_average_data[col].to_numpy()  # Use to_numpy() like Tab 2
                    # Validate data
                    if len(values) > 0 and not np.all(np.isnan(values)):
                        plot_data[wave] = values
                        all_values.extend(values)
                        print(f"[Tab 3] Added wavelength {wave}nm with {len(values)} points")
                        print(f"[Tab 3] Value range for {wave}nm: {min(values):.6f} to {max(values):.6f}")
                except (ValueError, KeyError) as e:
                    print(f"Error processing column {col}: {str(e)}")
                    continue
            
            if plot_data:
                print(f"\n[Tab 3] Plotting {len(plot_data)} wavelengths")
                print(f"[Tab 3] Time points: {len(data.time_points)} points")
                print(f"[Tab 3] Time range: {min(data.time_points)} to {max(data.time_points)}")
                
                # Calculate expected scale based on percentiles
                all_values = np.array(all_values)
                y_min, y_max = np.percentile(all_values, [1, 99])
                y_padding = (y_max - y_min) * 0.1
                expected_ymin = y_min - y_padding
                expected_ymax = y_max + y_padding
                print(f"\n[Tab 3] Expected y-axis scale: [{expected_ymin:.6f}, {expected_ymax:.6f}]")
                
                # Plot data and let plot_all_wavelengths handle scales
                self.plot_a.plot_all_wavelengths(
                    data.time_points,
                    plot_data,
                    clear=True,
                    respect_limits=False  # Let it calculate its own limits
                )
                
                # Check actual scale after plotting
                actual_xlim = self.plot_a.ax.get_xlim()
                actual_ylim = self.plot_a.ax.get_ylim()
                print(f"[Tab 3] Actual plot scales after plotting:")
                print(f"[Tab 3] X-axis: [{actual_xlim[0]:.6f}, {actual_xlim[1]:.6f}]")
                print(f"[Tab 3] Y-axis: [{actual_ylim[0]:.6f}, {actual_ylim[1]:.6f}]")
                
                # Restore or set default title for Plot A
                current_title = self.plot_a.ax.get_title()
                if not current_title or current_title == "":
                    self.plot_a.ax.set_title("absorption", pad=10, fontsize=12)
                
                # Initialize Plot C with empty view
                self.plot_c.clear()
                self.plot_c.ax.set_xlabel("Wavelength (nm)")
                self.plot_c.ax.set_ylabel("Average Intensity")
                self.plot_c.ax.set_title("Select time range in Plot A to calculate average")
                self.plot_c.ax.grid(True)
                
                # Setup the selector for time range selection
                self._setup_selector()
                
                # Check final scales after everything
                final_xlim = self.plot_a.ax.get_xlim()
                final_ylim = self.plot_a.ax.get_ylim()
                print(f"\n[Tab 3] Final plot scales:")
                print(f"[Tab 3] X-axis: [{final_xlim[0]:.6f}, {final_xlim[1]:.6f}]")
                print(f"[Tab 3] Y-axis: [{final_ylim[0]:.6f}, {final_ylim[1]:.6f}]")
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

    def _on_plot_a_draw(self, event):
        """Handle plot A draw event with debouncing."""
        if not self._sync_in_progress and self.plot_a.is_sync_enabled():
            self._sync_in_progress = True
            try:
                xlim, ylim = self.plot_a.get_current_view()
                self.plot_c.set_view(xlim, ylim)
            finally:
                self._sync_in_progress = False
                
    def _on_plot_c_draw(self, event):
        """Handle plot C draw event with debouncing."""
        if not self._sync_in_progress and self.plot_a.is_sync_enabled():
            self._sync_in_progress = True
            try:
                xlim, ylim = self.plot_c.get_current_view()
                self.plot_a.set_view(xlim, ylim)
            finally:
                self._sync_in_progress = False 

    def _on_apply_time_range(self):
        """Handle apply time range button click."""
        if self.current_data is None:
            return
            
        try:
            # Get time values from input boxes
            time_min = float(self.time_min_input.text())
            time_max = float(self.time_max_input.text())
            
            # Validate time range
            if time_min >= time_max:
                QMessageBox.warning(
                    self,
                    "Invalid Time Range",
                    "Minimum time must be less than maximum time."
                )
                return
                
            # Calculate average intensity for the selected time range
            time_points = np.array(self.current_data.time_points)
            time_mask = (time_points >= time_min) & (time_points <= time_max)
            
            if not any(time_mask):
                QMessageBox.warning(
                    self,
                    "Invalid Range",
                    "No data points found in the selected time range."
                )
                return
                
            wavelengths = []
            averages = []
            
            # Calculate averages for each wavelength
            for col in self.current_data.moving_average_data.columns[1:]:  # Skip time column
                try:
                    wave = float(col)
                    values = self.current_data.moving_average_data[col].values[time_mask]
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
                
                # Update both plots
                # Update selector in Plot A without changing the view
                if self.selector is not None:
                    # Store current view limits
                    current_xlim = self.plot_a.ax.get_xlim()
                    current_ylim = self.plot_a.ax.get_ylim()
                    
                    # Update the selector
                    self.selector.extents = (time_min, time_max)
                    
                    # Restore the original view
                    self.plot_a.ax.set_xlim(current_xlim)
                    self.plot_a.ax.set_ylim(current_ylim)
                    self.plot_a.canvas.draw()
                
                # Let plot_average_intensity handle its own scale calculation
                self.plot_c.plot_average_intensity(
                    wavelengths.tolist(),
                    averages.tolist(),
                    (time_min, time_max),
                    respect_limits=False  # Let it calculate its own limits
                )
            else:
                QMessageBox.warning(
                    self,
                    "No Data",
                    "No valid data for average intensity calculation in the selected range."
                )
                
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter valid numbers for time range."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error applying time range: {str(e)}"
            ) 