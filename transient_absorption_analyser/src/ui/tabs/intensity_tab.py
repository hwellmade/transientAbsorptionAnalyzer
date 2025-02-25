"""
Intensity tab implementation for average intensity plotting.
"""
from typing import Optional, Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
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
    QMessageBox,
    QScrollArea,
    QGroupBox,
    QColorDialog
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QColor
from matplotlib.widgets import RectangleSelector, SpanSelector

from ..plot_widget import PlotWidget
from ...core.data_processor import ProcessedData

class TimeSpanEntry(QWidget):
    """Widget for a single time span entry."""
    
    updated = Signal(dict)  # Emits when span is updated
    removed = Signal(int)   # Emits index when removed
    
    def __init__(self, index: int, initial_color: QColor):
        super().__init__()
        self.index = index
        self.current_color = initial_color
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)  # Compact layout
        
        # Time inputs
        self.min_input = QLineEdit()
        self.max_input = QLineEdit()
        self.min_input.setPlaceholderText("Min time")
        self.max_input.setPlaceholderText("Max time")
        self.min_input.setFixedWidth(80)
        self.max_input.setFixedWidth(80)
        
        # Color picker button
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(30, 20)
        self.update_color_button()
        
        # Apply and Remove buttons
        self.apply_btn = QPushButton("Apply")
        self.remove_btn = QPushButton("Remove")
        
        # Add to layout
        layout.addWidget(QLabel(f"Span {self.index + 1}:"))
        layout.addWidget(QLabel("Min:"))
        layout.addWidget(self.min_input)
        layout.addWidget(QLabel("Max:"))
        layout.addWidget(self.max_input)
        layout.addWidget(self.color_btn)
        layout.addWidget(self.apply_btn)
        layout.addWidget(self.remove_btn)
        layout.addStretch()
        
        # Connect signals
        self.color_btn.clicked.connect(self.show_color_dialog)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self.index))
        
    def show_color_dialog(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.update_color_button()
            
    def update_color_button(self):
        self.color_btn.setStyleSheet(
            f"background-color: {self.current_color.name()};"
            "border: 1px solid #999;"
        )
        
    def apply_changes(self):
        try:
            min_time = float(self.min_input.text())
            max_time = float(self.max_input.text())
            self.updated.emit({
                'index': self.index,
                'min_time': min_time,
                'max_time': max_time,
                'color': self.current_color
            })
        except ValueError:
            # Handle invalid input
            pass

class IntensityTab(QWidget):
    """Tab for intensity visualization."""
    
    MAX_TIME_SPANS = 10
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_data: Optional[ProcessedData] = None
        self.selector = None
        self._sync_in_progress = False
        self.time_spans = []  # List to store time span data
        self.time_span_entries = []  # List to store TimeSpanEntry widgets
        
        # Create plots first with sync_zoom=False
        self.plot_a = PlotWidget(sync_zoom=False)
        self.plot_c = PlotWidget(sync_zoom=False)
        
        # Configure plot sizes
        self.plot_a.setFixedSize(600, 400)
        self.plot_c.setFixedSize(600, 400)
        
        # Connect plot draw events for sync zoom
        self.plot_a.canvas.mpl_connect('draw_event', self._on_plot_a_draw)
        self.plot_c.canvas.mpl_connect('draw_event', self._on_plot_c_draw)
        
        self.setup_ui()
        self._initialize_default_view()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QHBoxLayout(self)
        
        # Left side container
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Plot A (top left)
        self.plot_a = PlotWidget(sync_zoom=True)
        left_layout.addWidget(self.plot_a)
        
        # Time span settings section (bottom left)
        time_span_group = QGroupBox("Time Span Selection")
        time_span_layout = QVBoxLayout(time_span_group)
        time_span_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add and Clear All buttons
        buttons_layout = QHBoxLayout()
        self.add_span_btn = QPushButton("Add Time Span")
        self.clear_all_btn = QPushButton("Clear All")
        self.add_span_btn.setStyleSheet(
            "QPushButton { padding: 5px 10px; background-color: #4CAF50; color: white; border-radius: 3px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.clear_all_btn.setStyleSheet(
            "QPushButton { padding: 5px 10px; background-color: #f44336; color: white; border-radius: 3px; }"
            "QPushButton:hover { background-color: #d32f2f; }"
        )
        buttons_layout.addWidget(self.add_span_btn)
        buttons_layout.addWidget(self.clear_all_btn)
        buttons_layout.addStretch()
        time_span_layout.addLayout(buttons_layout)
        
        # Scrollable area for time spans
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(200)  # Limit height
        
        self.time_spans_widget = QWidget()
        self.time_spans_layout = QVBoxLayout(self.time_spans_widget)
        self.time_spans_layout.setSpacing(2)
        self.time_spans_layout.setContentsMargins(2, 2, 2, 2)
        scroll.setWidget(self.time_spans_widget)
        time_span_layout.addWidget(scroll)
        
        # Add time span group to left layout
        left_layout.addWidget(time_span_group)
        
        # Right side - Plot C only
        self.plot_c = PlotWidget(sync_zoom=True)
        
        # Add containers to main layout
        main_layout.addWidget(left_container)
        main_layout.addWidget(self.plot_c)
        
        # Set stretch factors
        main_layout.setStretchFactor(left_container, 1)
        main_layout.setStretchFactor(self.plot_c, 1)
        
        # Connect signals
        self.add_span_btn.clicked.connect(self.add_time_span)
        self.clear_all_btn.clicked.connect(self.clear_all_spans)
        
        # Initialize first time span
        self.add_time_span()
        
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
        """Setup the span selector for manual time range selection."""
        self.selector = SpanSelector(
            self.plot_a.ax,
            self._on_select,
            'horizontal',
            useblit=True,
            props=dict(alpha=0.2, facecolor='gray'),
            interactive=True,
            drag_from_anywhere=True
        )
        
        # Add clear method to selector
        def clear():
            # Remove the span patch from the plot
            if hasattr(self.selector, 'rect'):
                self.selector.rect.remove()
            # Reset the selector's extents
            self.selector.extents = (0, 0)
            self.plot_a.canvas.draw()
        self.selector.clear = clear
        
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

    def update_data(self, data: ProcessedData):
        """Update displayed data."""
        self.current_data = data
        
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
                
                # Plot data in Plot A
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

    @Slot(str)
    def update_plot_titles(self, tag: str):
        """Update plot titles when tag changes in spectrum tab."""
        if tag:
            title = f"absorption: {tag}"
            self.plot_a.ax.set_title(title, pad=10, fontsize=12)
            self.plot_c.ax.set_title(f"average intensity v.s. wavelength: {tag}\ntime span: {int(self.plot_c.time_range[0])} - {int(self.plot_c.time_range[1])} ns" if self.plot_c.time_range else title, pad=10, fontsize=12)
            self.plot_a.canvas.draw()
            self.plot_c.canvas.draw()

    def add_time_span(self):
        """Add a new time span entry."""
        if len(self.time_span_entries) >= self.MAX_TIME_SPANS:
            return
            
        # Generate a new color from matplotlib color cycle
        colors = plt.cm.tab10.colors
        color_index = len(self.time_span_entries) % len(colors)
        color = QColor.fromRgbF(*colors[color_index])
        
        # Create new entry
        entry = TimeSpanEntry(len(self.time_span_entries), color)
        entry.updated.connect(self.update_time_span)
        entry.removed.connect(self.remove_time_span)
        
        # Add to layout and lists
        self.time_spans_layout.addWidget(entry)
        self.time_span_entries.append(entry)
        
        # Update Add button state
        self.add_span_btn.setEnabled(len(self.time_span_entries) < self.MAX_TIME_SPANS)
        
    def update_time_span(self, span_data: dict):
        """Update a time span and refresh plots."""
        index = span_data['index']
        
        # Update time spans list
        while len(self.time_spans) <= index:
            self.time_spans.append(None)
        self.time_spans[index] = span_data
        
        self.update_plots()
        
    def remove_time_span(self, index: int):
        """Remove a time span entry."""
        if 0 <= index < len(self.time_span_entries):
            # Remove widget
            entry = self.time_span_entries.pop(index)
            self.time_spans_layout.removeWidget(entry)
            entry.deleteLater()
            
            # Remove from time spans list
            if index < len(self.time_spans):
                self.time_spans.pop(index)
            
            # Update remaining indices
            for i, entry in enumerate(self.time_span_entries):
                entry.index = i
            
            # Enable Add button
            self.add_span_btn.setEnabled(True)
            
            self.update_plots()
            
    def clear_all_spans(self):
        """Clear all time span selections from plots without removing input rows."""
        # Clear the time spans list but keep the entries
        self.time_spans.clear()
        
        # Clear any drag-selected spans
        if hasattr(self, 'selector') and self.selector is not None:
            self.selector.clear()
            
        # Reset and redraw plots with base data
        if self.current_data:
            # Redraw Plot A with all wavelengths
            wavelength_columns = [col for col in self.current_data.moving_average_data.columns[1:]]
            plot_data = {}
            for col in wavelength_columns:
                try:
                    wave = float(col)
                    values = self.current_data.moving_average_data[col].to_numpy()
                    if len(values) > 0 and not np.all(np.isnan(values)):
                        plot_data[wave] = values
                except (ValueError, KeyError):
                    continue
                    
            if plot_data:
                self.plot_a.plot_all_wavelengths(
                    self.current_data.time_points,
                    plot_data,
                    clear=True,
                    respect_limits=False
                )
            
            # Clear Plot C and reset to default state
            self.plot_c.clear()
            self.plot_c.ax.set_xlabel("Wavelength (nm)")
            self.plot_c.ax.set_ylabel("Average Intensity")
            self.plot_c.ax.set_title("Select time range in Plot A to calculate average")
            self.plot_c.ax.grid(True)
            self.plot_c.canvas.draw()

    def update_plots(self):
        """Update both plots with current time spans."""
        if not self.current_data or not self.time_spans:
            return
            
        # Clear plots
        self.plot_a.ax.clear()
        self.plot_c.ax.clear()
        
        # Get MA data
        ma_data = self.current_data.moving_average_data
        time_points = ma_data.iloc[:, 0].to_numpy()
        
        # Clean up column names by removing spaces
        ma_data.columns = [col.strip() if isinstance(col, str) else col for col in ma_data.columns]
        wavelengths = [float(col) for col in ma_data.columns[1:]]
        
        # Debug info
        print(f"[Debug] Available columns in MA data (after cleanup): {ma_data.columns.tolist()}")
        print(f"[Debug] Number of time spans: {len(self.time_spans)}")
        
        # Plot A: Show all data with colored spans
        for col in ma_data.columns[1:]:  # Skip time column
            self.plot_a.ax.plot(time_points, ma_data[col], color='gray', alpha=0.5)
            
        # Add colored spans and plot averaged data
        for span in self.time_spans:
            if span is None:
                continue
                
            print(f"[Debug] Processing time span: {span['min_time']} - {span['max_time']}")
            
            # Add span to Plot A
            color = span['color'].getRgbF()[:3]  # Convert QColor to RGB
            self.plot_a.ax.axvspan(
                span['min_time'],
                span['max_time'],
                color=color,
                alpha=0.2
            )
            
            # Calculate and plot averaged data
            mask = (time_points >= span['min_time']) & (time_points <= span['max_time'])
            averages = []
            
            for wave in wavelengths:
                # Convert wavelength to match column format
                col_name = str(int(wave))  # Convert to integer string format
                try:
                    values = ma_data[col_name][mask]
                    avg = np.mean(values)
                    averages.append(avg)
                    print(f"[Debug] Calculated average for wavelength {col_name}: {avg}")
                except KeyError as e:
                    print(f"[Debug] Error accessing wavelength {col_name}: {str(e)}")
                    print(f"[Debug] Available columns: {ma_data.columns.tolist()}")
                    continue
                
            # Only plot if we have averages
            if averages:
                self.plot_c.ax.plot(
                    wavelengths,
                    averages,
                    color=color,
                    marker='o',  # Add circular markers
                    markersize=6,  # Set marker size
                    markerfacecolor=color,  # Fill color same as line
                    markeredgecolor='white',  # White edge for better visibility
                    markeredgewidth=1,  # Edge width
                    label=f"{int(span['min_time'])}-{int(span['max_time'])} ns"
                )
            else:
                print("[Debug] No averages calculated for this time span")
            
        # Update plot settings
        self.plot_a.ax.set_xlabel("Time (ns)")
        self.plot_a.ax.set_ylabel("Intensity")
        self.plot_a.ax.grid(True)
        
        self.plot_c.ax.set_xlabel("Wavelength (nm)")
        self.plot_c.ax.set_ylabel("Average Intensity")
        self.plot_c.ax.grid(True)
        self.plot_c.ax.legend()
        
        # Set title for Plot C
        if self.time_spans and any(span is not None for span in self.time_spans):
            self.plot_c.ax.set_title(
                "average intensity v.s. wavelength",
                pad=8
            )
        else:
            self.plot_c.ax.set_title("Select time range in Plot A to calculate average")
        
        # Redraw
        self.plot_a.canvas.draw()
        self.plot_c.canvas.draw() 