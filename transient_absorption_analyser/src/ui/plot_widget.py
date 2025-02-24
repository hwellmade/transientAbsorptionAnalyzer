"""
Custom plot widget combining Qt and Matplotlib functionality.
"""
from typing import Optional, Tuple, List
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox
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
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the widget's UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create matplotlib figure with reduced width (20% narrower)
        original_width = 8
        new_width = original_width * 0.8  # 20% narrower
        self.figure = Figure(figsize=(new_width, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        # Add sync checkbox if needed
        if self.sync_zoom:
            self.sync_check = QCheckBox("Sync Zoom")
            self.sync_check.setChecked(True)
            layout.addWidget(self.sync_check)
        
        # Add matplotlib widgets
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)
        self.ax.grid(True)
        
        # Adjust subplot parameters to give specified padding
        # Increase left margin to accommodate y-label
        self.figure.subplots_adjust(left=0.15, right=0.95, bottom=0.12, top=0.95)
        
    def plot_all_wavelengths(
        self,
        time_points: List[float],
        data: dict,
        clear: bool = True
    ):
        """Plot all wavelengths vs time."""
        if clear:
            self.ax.clear()
            
        # Debug info
        print(f"Plotting {len(data)} wavelengths")
        print(f"Time points range: {min(time_points)} to {max(time_points)}")
        
        # Plot each wavelength
        all_values = []
        for wavelength, values in data.items():
            # Debug info
            value_range = np.max(values) - np.min(values)
            print(f"Wavelength {wavelength}nm - Value range: {value_range}")
            
            self.ax.plot(
                time_points,
                values,
                label=f"{wavelength} nm"
            )
            all_values.extend(values)
            
        # Calculate proper axis limits with padding
        all_values = np.array(all_values)
        ymin, ymax = np.min(all_values), np.max(all_values)
        y_padding = (ymax - ymin) * 0.1  # 10% padding
        
        xmin, xmax = min(time_points), max(time_points)
        x_padding = (xmax - xmin) * 0.05  # 5% padding
        
        # Set limits with padding
        self.ax.set_xlim(xmin - x_padding, xmax + x_padding)
        self.ax.set_ylim(ymin - y_padding, ymax + y_padding)
        
        # Set labels and grid
        self.ax.set_xlabel("Time (ns)", fontsize=10, labelpad=5)
        self.ax.set_ylabel("Intensity (a.u.)", fontsize=10, labelpad=10)  # Increased labelpad
        self.ax.set_title("absorption", pad=10)
        self.ax.legend(fontsize=8)
        self.ax.grid(True)
        
        # Adjust layout and draw
        self.figure.subplots_adjust(left=0.15, right=0.95, bottom=0.12, top=0.95)
        self.canvas.draw()
        
    def plot_highlighted_wavelengths(
        self,
        time_points: List[float],
        data: dict,
        highlighted_wavelengths: List[float],
        clear: bool = True
    ):
        """Plot with multiple wavelengths highlighted."""
        if clear:
            self.ax.clear()
            
        # Debug info
        print(f"Highlighting {len(highlighted_wavelengths)} wavelengths")
        print(f"Time points range: {min(time_points)} to {max(time_points)}")
            
        # Plot all wavelengths in grey first
        all_values = []
        for wave, values in data.items():
            all_values.extend(values)
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
        
        # Calculate proper axis limits with padding
        ymin, ymax = np.min(all_values), np.max(all_values)
        y_padding = (ymax - ymin) * 0.1  # 10% padding
        
        xmin, xmax = min(time_points), max(time_points)
        x_padding = (xmax - xmin) * 0.05  # 5% padding
        
        # Set limits with padding
        self.ax.set_xlim(xmin - x_padding, xmax + x_padding)
        self.ax.set_ylim(ymin - y_padding, ymax + y_padding)
        
        # Set labels and grid
        self.ax.set_xlabel("Time (ns)", fontsize=10, labelpad=5)
        self.ax.set_ylabel("Intensity (a.u.)", fontsize=10, labelpad=10)  # Increased labelpad
        self.ax.set_title("absorption", pad=10)
        self.ax.legend(fontsize=8)
        self.ax.grid(True)
        
        # Adjust layout and draw
        self.figure.subplots_adjust(left=0.15, right=0.95, bottom=0.12, top=0.95)  # Updated margins
        self.canvas.draw()
        
    def plot_average_intensity(
        self,
        wavelengths: List[float],
        averages: List[float],
        time_range: Tuple[float, float],
        clear: bool = True
    ):
        """Plot average intensity vs wavelength."""
        if clear:
            self.ax.clear()
            
        self.ax.plot(
            wavelengths,
            averages,
            'bo-'
        )
        
        # Calculate proper axis limits with padding
        ymin, ymax = min(averages), max(averages)
        y_padding = (ymax - ymin) * 0.1  # 10% padding
        
        xmin, xmax = min(wavelengths), max(wavelengths)
        x_padding = (xmax - xmin) * 0.05  # 5% padding
        
        # Set limits with padding
        self.ax.set_xlim(xmin - x_padding, xmax + x_padding)
        self.ax.set_ylim(ymin - y_padding, ymax + y_padding)
        
        self.time_range = time_range
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Average Intensity")
        self.ax.set_title(f"average intensity v.s. wavelength\ntime span: {time_range[0]:.2f} - {time_range[1]:.2f} ns")
        self.ax.grid(True)
        
        # Force update
        self.figure.tight_layout()
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