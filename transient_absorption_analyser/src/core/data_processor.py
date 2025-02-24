"""
Core data processing functionality for the Transient Absorption Analyser.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from PySide6.QtCore import QObject, Signal

class ProcessedData:
    """Container for processed data."""
    
    def __init__(
        self,
        signal_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame],
        signal_common: Optional[pd.DataFrame],
        dark_common: Optional[pd.DataFrame],
        common_data: pd.DataFrame,
        moving_average_data: pd.DataFrame,  # New parameter for MA data
        wavelengths: List[float],
        time_points: List[float],
        moving_average_window: int
    ):
        self.signal_data = signal_data
        self.reference_data = reference_data
        self.signal_common = signal_common
        self.dark_common = dark_common
        self.common_data = common_data
        self.moving_average_data = moving_average_data  # Store MA data separately
        self.wavelengths = wavelengths
        self.time_points = time_points
        self.moving_average_window = moving_average_window
        
    def get_summary(self) -> str:
        """Get summary of processed data."""
        return (
            f"Data processing complete:\n"
            f"- Number of wavelengths: {len(self.wavelengths)}\n"
            f"- Number of time points: {len(self.time_points)}\n"
            f"- Moving average window: {self.moving_average_window}"
        )

class DataProcessor(QObject):
    """Handles data processing operations."""
    
    # Signals
    processing_complete = Signal(ProcessedData)
    processing_error = Signal(str)
    processing_progress = Signal(int)  # 0-100%
    
    def __init__(self):
        super().__init__()
        
    def process_files(
        self,
        signal_path: str,
        reference_path: Optional[str],
        window_size: int
    ) -> Optional[ProcessedData]:
        """
        Process signal and reference files.
        
        Args:
            signal_path: Path to signal data file
            reference_path: Optional path to reference data file
            window_size: Moving average window size
            
        Returns:
            ProcessedData object if successful, None otherwise
        """
        try:
            # Load data
            self.processing_progress.emit(10)
            signal_data = self._load_data(signal_path)
            reference_data = self._load_data(reference_path) if reference_path else None
            
            # Validate data
            self._validate_data(signal_data, reference_data, window_size)
            self.processing_progress.emit(30)
            
            # Find common parameters and calculate difference
            common_data, signal_common, dark_common = self._find_common_data(signal_data, reference_data)
            self.processing_progress.emit(50)
            
            # Process data
            raw_data, ma_data = self._process_data(common_data, window_size)
            self.processing_progress.emit(80)
            
            # Create result object
            result = ProcessedData(
                signal_data=signal_data,
                reference_data=reference_data,
                signal_common=signal_common,
                dark_common=dark_common,
                common_data=raw_data,
                moving_average_data=ma_data,
                wavelengths=self._get_wavelengths(raw_data),
                time_points=self._get_time_points(raw_data),
                moving_average_window=window_size
            )
            
            self.processing_progress.emit(100)
            self.processing_complete.emit(result)
            return result
            
        except Exception as e:
            self.processing_error.emit(str(e))
            return None
            
    def _load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from file."""
        try:
            # Check file extension
            if not any(file_path.lower().endswith(ext) for ext in ['.csv', '.xls', '.xlsx', '.txt']):
                raise ValueError(
                    f"Unsupported file format. Please use one of the following:\n"
                    f"- CSV files (.csv)\n"
                    f"- Excel files (.xls, .xlsx)\n"
                    f"- Tab-delimited text files (.txt)"
                )

            # Load data based on file extension
            try:
                if file_path.lower().endswith('.csv'):
                    # Try with different decimal and thousand separators
                    try:
                        data = pd.read_csv(file_path, encoding='utf-8', decimal='.', thousands=None)
                    except:
                        try:
                            data = pd.read_csv(file_path, encoding='utf-8', decimal=',', thousands=None)
                        except:
                            data = pd.read_csv(file_path, encoding='utf-8')
                elif file_path.lower().endswith(('.xls', '.xlsx')):
                    data = pd.read_excel(file_path, engine='openpyxl')
                elif file_path.lower().endswith('.txt'):
                    # Try different delimiters and decimal separators
                    try:
                        data = pd.read_csv(file_path, delimiter='\t', decimal='.', encoding='utf-8')
                    except:
                        try:
                            data = pd.read_csv(file_path, delimiter='\t', decimal=',', encoding='utf-8')
                        except:
                            try:
                                data = pd.read_csv(file_path, delimiter=',', decimal='.', encoding='utf-8')
                            except:
                                try:
                                    data = pd.read_csv(file_path, delimiter=',', decimal=',', encoding='utf-8')
                                except:
                                    data = pd.read_csv(file_path, delimiter=None, encoding='utf-8')
            except UnicodeDecodeError:
                # Try different encoding if UTF-8 fails
                if file_path.lower().endswith('.csv') or file_path.lower().endswith('.txt'):
                    try:
                        data = pd.read_csv(file_path, encoding='latin1', decimal='.')
                    except:
                        data = pd.read_csv(file_path, encoding='latin1', decimal=',')
                else:
                    raise
            except Exception as e:
                raise ValueError(f"Error reading file: {str(e)}")

            # Validate data structure
            if data.empty:
                raise ValueError("The file is empty")

            # Check if we have at least two columns (time and one wavelength)
            if len(data.columns) < 2:
                raise ValueError(
                    "Invalid data format. The file should contain:\n"
                    "- First column: Time points\n"
                    "- Additional columns: Wavelength measurements"
                )

            # Convert any comma-formatted numbers in column names to dots
            data.columns = [str(col).replace(',', '.') if isinstance(col, str) else col for col in data.columns]

            # Try to convert column names to float (except first column)
            try:
                wavelengths = []
                for col in data.columns[1:]:
                    try:
                        # Handle both dot and comma decimal separators in column names
                        col_str = str(col).replace(',', '.')
                        wavelengths.append(float(col_str))
                    except ValueError:
                        raise ValueError(
                            f"Invalid column header '{col}'. All columns except the first should be wavelength values.\n"
                            "Example format:\n"
                            "Time,532.0,533.0,534.0\n"
                            "0.0,0.1,0.2,0.3\n"
                            "1.0,0.2,0.3,0.4"
                        )
            except Exception as e:
                raise ValueError(str(e))

            # Try to convert all data to numeric, handling both dot and comma decimals
            try:
                # First column (time)
                time_col = data.columns[0]
                data[time_col] = pd.to_numeric(data[time_col].astype(str).str.replace(',', '.'), errors='raise')
                
                # Wavelength columns
                for col in data.columns[1:]:
                    data[col] = pd.to_numeric(data[col].astype(str).str.replace(',', '.'), errors='raise')
            except Exception as e:
                raise ValueError(
                    f"Invalid data values. All values must be numeric.\n"
                    f"Error details: {str(e)}\n"
                    "Please check your data file for non-numeric values."
                )

            return data

        except FileNotFoundError:
            raise ValueError(f"Could not find the file:\n{file_path}")
        except PermissionError:
            raise ValueError(f"Permission denied when trying to access:\n{file_path}")
        except pd.errors.EmptyDataError:
            raise ValueError(f"The file is empty:\n{file_path}")
        except Exception as e:
            raise ValueError(
                f"Error loading file:\n{file_path}\n\n"
                f"Details: {str(e)}\n\n"
                f"Please ensure:\n"
                f"1. The file is not corrupted\n"
                f"2. The file has the correct format\n"
                f"3. The first row contains headers (Time, wavelengths)\n"
                f"4. All data values are numeric\n"
                f"5. Numbers use either dots (.) or commas (,) as decimal separators"
            )
            
    def _validate_data(
        self,
        signal_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame],
        window_size: int
    ) -> None:
        """Validate input data."""
        if signal_data is None or signal_data.empty:
            raise ValueError("Signal data is empty")
            
        if len(signal_data) < window_size:
            raise ValueError(
                f"Not enough data points ({len(signal_data)}) "
                f"for moving average window size ({window_size})"
            )
            
    def _find_common_data(
        self,
        signal_data: pd.DataFrame,
        reference_data: Optional[pd.DataFrame]
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Find common wavelengths and time points."""
        if reference_data is None:
            return signal_data, None, None
            
        # Round wavelengths for comparison
        signal_waves = [round(float(col), 2) for col in signal_data.columns[1:]]
        ref_waves = [round(float(col), 2) for col in reference_data.columns[1:]]
        
        # Find common wavelengths
        common_waves = set(signal_waves) & set(ref_waves)
        if not common_waves:
            raise ValueError("No common wavelengths found between signal and reference")
            
        # Find common time points
        common_times = set(signal_data.iloc[:, 0]) & set(reference_data.iloc[:, 0])
        if not common_times:
            raise ValueError("No common time points found between signal and reference")
            
        # Filter data
        signal_filtered = signal_data[
            signal_data.iloc[:, 0].isin(common_times)
        ]
        reference_filtered = reference_data[
            reference_data.iloc[:, 0].isin(common_times)
        ]
        
        # Create result DataFrame
        result = signal_filtered.copy()
        for wave in common_waves:
            sig_col = signal_filtered.columns[
                signal_waves.index(wave) + 1
            ]
            ref_col = reference_filtered.columns[
                ref_waves.index(wave) + 1
            ]
            result[sig_col] = signal_filtered[sig_col] - reference_filtered[ref_col]
            
        return result, signal_filtered, reference_filtered
        
    def _process_data(
        self,
        data: pd.DataFrame,
        window_size: int
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply moving average to data and return both raw and processed data."""
        raw_data = data.copy()
        ma_data = data.copy()
        
        # Apply moving average to each wavelength column in ma_data
        for col in ma_data.columns[1:]:  # Skip time column
            ma_data[col] = self._moving_average(
                ma_data[col].values,
                window_size
            )
            
        return raw_data, ma_data
        
    def _moving_average(
        self,
        data: np.ndarray,
        window_size: int
    ) -> np.ndarray:
        """Calculate moving average."""
        return np.convolve(
            data,
            np.ones(window_size) / window_size,
            mode='same'
        )
        
    def _get_wavelengths(self, data: pd.DataFrame) -> List[float]:
        """Extract wavelengths from data."""
        return [float(col) for col in data.columns[1:]]
        
    def _get_time_points(self, data: pd.DataFrame) -> List[float]:
        """Extract time points from data."""
        return data.iloc[:, 0].tolist() 