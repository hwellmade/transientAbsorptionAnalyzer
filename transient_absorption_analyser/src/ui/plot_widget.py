"""
Custom plot widget combining Qt and Matplotlib functionality.
"""
from typing import Optional, Tuple, List
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QSizePolicy
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT
)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class PlotWidget(QWidget):
    """Widget for displaying interactive matplotlib plots."""
    
    def __init__(
        self,
        title: str = "",
        sync_zoom: bool = True,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.title = title
        self.sync_zoom = sync_zoom
        self.highlighted_wavelength = None
        self.time_range = None
        
        # Create the main layout first
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib components with updated size and DPI
        self.figure = Figure(figsize=(6, 4), dpi=100)  # Reduced from (10, 6) to better fit the layout
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = self.figure.add_subplot(111)
        
        # Configure the canvas
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        
        # Add widgets to layout
        if self.sync_zoom:
            self.sync_check = QCheckBox("Sync Zoom")
            self.sync_check.setChecked(True)
            self.layout.addWidget(self.sync_check)
        
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        
        # Configure plot after widget setup
        self._setup_plot()
        
    def _setup_plot(self):
        """Setup the plot configuration."""
        # Configure figure margins with more space for labels and title
        self.figure.subplots_adjust(
            left=0.2,     # Left margin for y-label
            right=0.95,   # Right margin
            top=0.85,     # Reduced top margin to bring title closer (was 0.90)
            bottom=0.12,  # Bottom margin for x-label
            wspace=0.2,   # Width spacing
            hspace=0.1    # Height spacing
        )
        
        # Set initial plot properties
        if self.title:
            self.ax.set_title(self.title, pad=8)  # Reduced padding (was 15)
        self.ax.grid(True)
        
    def plot_all_wavelengths(
        self,
        time_points: List[float],
        data: dict,
        clear: bool = True,
        respect_limits: bool = False
    ):
        """Plot all wavelengths vs time."""
        if clear:
            # Store current limits if needed
            if respect_limits:
                curr_xlim = self.ax.get_xlim()
                curr_ylim = self.ax.get_ylim()
            self.ax.clear()
            if respect_limits:
                self.ax.set_xlim(curr_xlim)
                self.ax.set_ylim(curr_ylim)
            
        # Debug info
        print(f"Plotting {len(data)} wavelengths")
        print(f"Time points range: {min(time_points)} to {max(time_points)}")
        
        # Plot each wavelength and collect all values for scale calculation
        all_values = []
        for wavelength, values in data.items():
            self.ax.plot(
                time_points,
                values,
                label=f"{wavelength} nm"
            )
            all_values.extend(values)
            
        # Only set limits if not respecting external limits
        if not respect_limits:
            # Calculate proper axis limits using min/max
            all_values = np.array(all_values)
            y_min = np.min(all_values)
            y_max = np.max(all_values)
            
            # Add padding proportional to the range
            y_padding = (y_max - y_min) * 0.1
            
            # Set X limits with padding
            xmin, xmax = min(time_points), max(time_points)
            x_padding = (xmax - xmin) * 0.05
            self.ax.set_xlim(xmin - x_padding, xmax + x_padding)
            
            # Set Y limits with padding
            self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
            
            # Debug print the actual limits being set
            print(f"Y-axis range:")
            print(f"Raw range: [{y_min:.6f}, {y_max:.6f}]")
            print(f"With padding: [{y_min - y_padding:.6f}, {y_max + y_padding:.6f}]")
        
        # Set labels and grid
        self.ax.set_xlabel("Time (ns)", fontsize=10, labelpad=8)
        self.ax.set_ylabel("Intensity (a.u.)", fontsize=10, labelpad=15)
        self.ax.grid(True)
        
        # Place legend outside
        self.ax.legend(
            fontsize=8,
            bbox_to_anchor=(1.02, 1),
            loc='upper left',
            borderaxespad=0
        )
        
        # Use the same margins
        self.figure.subplots_adjust(
            left=0.2,
            right=0.85,
            top=0.85,
            bottom=0.15
        )
        
        # Restore title if it exists
        if self.title:
            self.ax.set_title(self.title, pad=8)
            
        self.canvas.draw()
        
    def plot_highlighted_wavelengths(
        self,
        time_points: List[float],
        data: dict,
        highlighted_wavelengths: List[float],
        clear: bool = True
    ):
        """Plot with multiple wavelengths highlighted."""
        # Store current limits and title before clearing
        curr_xlim = self.ax.get_xlim()
        curr_ylim = self.ax.get_ylim()
        curr_title = self.ax.get_title()  # Store the current title
        print(f"Stored limits before highlighting - Y: [{curr_ylim[0]:.6f}, {curr_ylim[1]:.6f}]")
        
        if clear:
            self.ax.clear()
            
        # Debug info
        print(f"Highlighting {len(highlighted_wavelengths)} wavelengths")
        print(f"Time points range: {min(time_points)} to {max(time_points)}")
            
        # Plot all wavelengths in grey first
        for wave, values in data.items():
            if wave not in highlighted_wavelengths:
                self.ax.plot(
                    time_points,
                    values,
                    color='grey',
                    alpha=0.3,
                    zorder=1,  # Ensure grey lines are in the background
                    label='Other wavelengths' if wave == list(data.keys())[0] else None  # Label only first grey line
                )
        
        # Plot highlighted wavelengths in different colors
        if highlighted_wavelengths:
            # Use a color cycle for multiple highlights
            colors = plt.cm.tab10(np.linspace(0, 1, len(highlighted_wavelengths)))
            for wave, color in zip(highlighted_wavelengths, colors):
                if wave in data:
                    values = data[wave]
                    value_range = max(values) - min(values)
                    print(f"Highlighted wavelength {wave}nm value range: {value_range}")
                    
                    self.ax.plot(
                        time_points,
                        values,
                        color=color,
                        label=f"{wave} nm",
                        linewidth=2,
                        zorder=2  # Ensure highlighted lines are in the foreground
                    )
        
        # Restore the original limits
        self.ax.set_xlim(curr_xlim)
        self.ax.set_ylim(curr_ylim)
        print(f"Restored limits after highlighting - Y: [{curr_ylim[0]:.6f}, {curr_ylim[1]:.6f}]")
        
        # Set labels and grid with increased padding
        self.ax.set_xlabel("Time (ns)", fontsize=10, labelpad=5)
        self.ax.set_ylabel("Intensity (a.u.)", fontsize=10, labelpad=15)  # Increased labelpad
        self.ax.grid(True)
        
        # Update legend based on whether we have highlights
        if highlighted_wavelengths:
            self.ax.legend(fontsize=8, loc='upper right')  # Show legend with highlighted wavelengths
        else:
            self.ax.legend(fontsize=8, loc='upper right', labels=['All wavelengths'])  # Simple legend when no highlights
        
        # Use the same margins as _setup_plot
        self.figure.subplots_adjust(
            left=0.2,     # Match the new left margin
            right=0.95,
            top=0.85,
            bottom=0.12
        )
        
        # Restore the title with the same formatting
        if curr_title:
            self.ax.set_title(curr_title, pad=10, fontsize=12)
        else:
            self.ax.set_title("absorption", pad=10, fontsize=12)  # Set default title if none exists
            
        self.canvas.draw()
        
    def plot_average_intensity(
        self,
        wavelengths: List[float],
        averages: List[float],
        time_range: Tuple[float, float],
        respect_limits: bool = False
    ):
        """Plot average intensity vs wavelength."""
        # Store current limits if needed
        if respect_limits:
            curr_xlim = self.ax.get_xlim()
            curr_ylim = self.ax.get_ylim()
        self.ax.clear()
        if respect_limits:
            self.ax.set_xlim(curr_xlim)
            self.ax.set_ylim(curr_ylim)
            
        self.ax.plot(
            wavelengths,
            averages,
            'bo-'
        )
        
        # Only set limits if not respecting external limits
        if not respect_limits:
            # Calculate proper axis limits with padding
            ymin, ymax = min(averages), max(averages)
            y_padding = (ymax - ymin) * 0.1
            
            xmin, xmax = min(wavelengths), max(wavelengths)
            x_padding = (xmax - xmin) * 0.05
            
            self.ax.set_xlim(xmin - x_padding, xmax + x_padding)
            self.ax.set_ylim(ymin - y_padding, ymax + y_padding)
        
        self.time_range = time_range
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Average Intensity")
        self.ax.set_title(
            f"average intensity v.s. wavelength\ntime span: {int(time_range[0])} - {int(time_range[1])} ns",
            pad=8
        )
        self.ax.grid(True)
        
        # Use updated margins
        self.figure.subplots_adjust(
            left=0.2,
            right=0.95,
            top=0.85,
            bottom=0.12
        )
        
        self.canvas.draw()
        
    def get_current_view(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Get current axis limits."""
        return (
            self.ax.get_xlim(),
            self.ax.get_ylim()
        )
        
    def set_view(
        self,
        xlim: Tuple[float, float],
        ylim: Tuple[float, float]
    ):
        """Set axis limits."""
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.canvas.draw()
        
    def is_sync_enabled(self) -> bool:
        """Check if zoom sync is enabled."""
        return hasattr(self, 'sync_check') and self.sync_check.isChecked()
        
    def clear(self):
        """Clear the plot."""
        self.ax.clear()
        self.ax.grid(True)
        self.canvas.draw() 