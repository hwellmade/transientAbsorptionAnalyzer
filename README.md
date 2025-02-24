# Transient Absorption Analyser

A Python application for analyzing transient absorption spectroscopy data with an intuitive graphical user interface.

## Repository

```bash
https://github.com/hwellmade/transientAbsorptionAnalyzer.git
```

## Requirements

For running the standalone executable (.exe):
- Windows 10/11
- No other requirements - everything is included!

For running from source:
- Python 3.11 or higher
- Required Python packages (installed automatically)
- Windows 10/11 (for run.bat) or any OS (for Python direct run)

## Features

- Interactive data visualization with synchronized plots
- Load and process signal and reference data files
- Moving average smoothing with configurable window size
- Multiple plot types:
  - All wavelengths over time
  - Highlighted wavelength comparison
  - Time range selection and averaging
  - Average intensity vs wavelength
- Flexible data export options
- Synchronized plot zooming and scaling

## Installation

### Option 1: Standalone Executable (Recommended for Windows Users)

This is the easiest way to run the application:
1. Download `TransientAbsorptionAnalyser.exe` from the [releases page](https://github.com/hwellmade/transientAbsorptionAnalyzer/releases)
2. Double-click to run - no installation needed!

Benefits:
- No Python installation required
- All dependencies included
- Works immediately
- No configuration needed

### Option 2: Simple Python Installation

For users who prefer to run from source or need cross-platform support:

1. Download the repository:
   ```bash
   git clone https://github.com/hwellmade/transientAbsorptionAnalyzer.git
   cd transientAbsorptionAnalyzer
   ```
   Or download ZIP from [GitHub](https://github.com/hwellmade/transientAbsorptionAnalyzer)

2. Install Python:
   - Download Python 3.11 or higher from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"
   - Verify installation by opening a terminal/command prompt and running:
     ```bash
     python --version
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   - Double-click `run.bat` (Windows)
   OR
   - Open terminal/command prompt and run:
   ```bash
   python -m transient_absorption_analyser.src.main
   ```

### Option 3: Developer Installation (with Poetry)

For developers who want to contribute or modify the code:

1. Install Python 3.11 from [python.org](https://www.python.org/downloads/)

2. Install Poetry (package manager):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   Or on Windows PowerShell:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

3. Clone the repository:
   ```bash
   git clone https://github.com/hwellmade/transientAbsorptionAnalyzer.git
   cd transientAbsorptionAnalyzer
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Run the application:
   ```bash
   poetry run analyzer
   ```

## Usage

### If installed with Python:

1. Open a terminal/command prompt in the project directory
2. Run the application:
   ```bash
   poetry run analyzer
   ```
   Or use the provided `run.bat` file (Windows)

### If using standalone executable:

Simply double-click the `TransientAbsorptionAnalyser.exe` file.

## Data Format Requirements

The application accepts data files in the following formats:
- CSV (.csv)
- Excel (.xls, .xlsx)
- Text files (.txt)

Expected data structure:
- First column: Time values (ns)
- Remaining columns: Wavelength measurements
- Column headers should contain wavelength values (e.g., 532.0, 533.0, etc.)

Example format:
```
Time,532.0,533.0,534.0
0.0,0.1,0.2,0.3
1.0,0.2,0.3,0.4
```

## Using the Application

1. **Load Data Tab**
   - Upload signal file (required)
   - Upload dark file (optional)
   - Set moving average window size (N)
   - Click "Load and Go"

2. **Spectrum Tab**
   - View all wavelength curves
   - Select specific wavelengths to highlight
   - Use sync zoom for synchronized plot navigation

3. **Intensity Tab**
   - Set time range by dragging or manual input
   - View average intensity vs wavelength
   - Add tags to plots

4. **Export**
   - Click the Export button to save:
     - All plots as PNG files
     - Processed data as CSV files
     - Time-averaged data

## Troubleshooting

Common issues and solutions:

1. **File Loading Issues**
   - Ensure data files match the expected format
   - Check for non-numeric values in data columns
   - Verify column headers are wavelength values

2. **Display Issues**
   - Try resizing the window
   - Use the reset view button in the plot toolbar

3. **Performance Issues**
   - Reduce the data file size
   - Adjust the moving average window size

## Support

For bug reports or feature requests, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Development

### Project Structure
```
transient_absorption_analyser/
├── src/
│   ├── ui/
│   │   ├── main_window.py
│   │   └── tabs/
│   │       ├── load_tab.py
│   │       ├── spectrum_tab.py
│   │       └── intensity_tab.py
│   ├── core/
│   │   ├── data_processor.py
│   │   ├── plot_manager.py
│   │   └── export_manager.py
│   └── utils/
│       ├── validators.py
│       └── constants.py
├── tests/
├── pyproject.toml
├── poetry.lock
└── README.md
```

### Running Tests
```bash
poetry run pytest
```

### Code Style
This project uses:
- Black for code formatting
- Flake8 for style guide enforcement
- MyPy for type checking

To format code:
```bash
poetry run black .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 