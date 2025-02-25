"""
Export management functionality for the Transient Absorption Analyser.
"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
from typing import Dict, Optional, Union

import pandas as pd
from matplotlib.figure import Figure
from transient_absorption_analyser.src.core.data_processor import ProcessedData
from transient_absorption_analyser.src.ui.plot_widget import PlotWidget

class ExportManager:
    """Manages data and figure exports."""
    
    def __init__(self):
        self.current_export_dir: Optional[Path] = None
        self.current_data_hash: Optional[str] = None
        
    def export_all(
        self,
        base_path: str,
        data: Union[ProcessedData, Dict[str, pd.DataFrame]],
        plots: Dict[str, PlotWidget],
        moving_average_window: int
    ) -> Path:
        """
        Export all data and plots.
        
        Args:
            base_path: Base directory for export
            data: ProcessedData object or dictionary of data frames to export
            plots: Dictionary of plot widgets
            moving_average_window: Moving average window size
            
        Returns:
            Path to export directory
        """
        try:
            # Convert ProcessedData to dictionary if needed
            data_dict = self._convert_to_dict(data)
            
            # Calculate new data hash
            new_hash = self._calculate_data_hash(data_dict)
            
            # Create new export directory if needed
            if (self.current_export_dir is None or 
                self.current_data_hash != new_hash):
                
                self.current_export_dir = self._generate_export_path(
                    base_path,
                    moving_average_window
                )
                self.current_data_hash = new_hash
                
                # Create directory structure
                Path(self.current_export_dir).mkdir(parents=True, exist_ok=True)
                Path(self.current_export_dir / 'data').mkdir(exist_ok=True)
                Path(self.current_export_dir / 'figures').mkdir(exist_ok=True)
                
                # Export data files
                self._export_data_files(data_dict)
            
            # Always export figures
            self._export_figures(plots)
            
            return self.current_export_dir
            
        except Exception as e:
            print(f"Error in export_all: {str(e)}")
            raise
        
    def _convert_to_dict(
        self,
        data: Union[ProcessedData, Dict[str, pd.DataFrame]]
    ) -> Dict[str, pd.DataFrame]:
        """Convert ProcessedData to dictionary if needed."""
        if isinstance(data, ProcessedData):
            return {
                'signal': data.signal_data,
                'reference': data.reference_data,
                'signal_common': data.signal_common,
                'dark_common': data.dark_common,
                'difference': data.common_data,
                'ma': data.moving_average_data  # Now using the separate MA data
            }
        return data
        
    def _generate_export_path(self, base_path: str, window_size: int) -> Path:
        """Generate unique export directory path."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_name = f"{timestamp}_N{window_size}"
        # Ensure base_path is a proper Path object and resolve it
        return Path(base_path).resolve() / dir_name
        
    def _calculate_data_hash(self, data_dict: Dict[str, pd.DataFrame]) -> str:
        """Calculate hash of data to detect changes."""
        # Convert numerical data to string with fixed precision
        data_str = json.dumps({
            key: df.round(10).to_json() if df is not None else None
            for key, df in data_dict.items()
        })
        return hashlib.md5(data_str.encode()).hexdigest()
        
    def _export_data_files(self, data_dict: Dict[str, pd.DataFrame]):
        """Export data files if they don't exist."""
        try:
            data_dir = Path(self.current_export_dir) / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Define file mapping
            file_mapping = {
                'signal': 'signal.csv',
                'reference': 'reference_dark.csv',
                'signal_common': 'common_signal.csv',
                'dark_common': 'common_reference_dark.csv',
                'difference': 'common_signal_minus_common_reference.csv',
                'ma': 'moving_average.csv'
            }
            
            # Export each data file if it doesn't exist
            for key, filename in file_mapping.items():
                if key in data_dict and data_dict[key] is not None:
                    file_path = data_dir / filename
                    if not file_path.exists():
                        data_dict[key].to_csv(file_path, index=False)
        except Exception as e:
            print(f"Error in _export_data_files: {str(e)}")
            raise
                    
    def _export_figures(self, plots: Dict[str, PlotWidget]):
        """Export figures with timestamp for uniqueness."""
        try:
            fig_dir = Path(self.current_export_dir) / 'figures'
            fig_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%H%M%S')
            
            for plot_name, plot_widget in plots.items():
                if plot_widget is None:
                    continue
                
                # Get the matplotlib figure from the widget
                fig = plot_widget.figure
                
                # Generate base name based on plot type
                if plot_name == 'plot_B' and hasattr(plot_widget, 'highlighted_wavelength'):
                    base_name = f"curve_{plot_widget.highlighted_wavelength}_{timestamp}"
                elif plot_name == 'plot_C' and hasattr(plot_widget, 'time_range') and plot_widget.time_range is not None:
                    base_name = (
                        f"avg_signal_vs_wavelength_time_"
                        f"{int(plot_widget.time_range[0])}_{int(plot_widget.time_range[1])}ns_{timestamp}"
                    )
                elif plot_name == 'plot_A_intensity':  # New case for Plot A from Intensity tab
                    base_name = f"time_range_selection_{timestamp}"
                else:
                    base_name = f"all_spectrum_{timestamp}"
                
                # Save in PNG format
                save_path = fig_dir / f"{base_name}.png"
                print(f"Saving figure to: {save_path}")
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
        except Exception as e:
            print(f"Error in _export_figures: {str(e)}")
            raise 