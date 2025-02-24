# Transient Absorption Analyser

A Python application for analyzing transient absorption spectroscopy data with an intuitive graphical user interface.

## Features

- Load and process signal and reference data files
- Automatic wavelength and time parameter matching
- Moving average smoothing with configurable window size
- Interactive data visualization
- Multiple plot types:
  - All wavelengths over time
  - Highlighted wavelength comparison
  - Average intensity vs wavelength
- Flexible data export options
- Synchronized plot zooming and scaling

## Installation

1. Make sure you have Python 3.8 or newer installed
2. Install Poetry (package manager) if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TransientAbsorptionAnalyser.git
   cd TransientAbsorptionAnalyser
   ```
4. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

1. Activate the poetry environment:
   ```bash
   poetry shell
   ```

2. Run the application:
   ```bash
   poetry run analyzer
   ```

## Data Format

The application accepts data files in the following formats:
- CSV (.csv)
- Excel (.xls, .xlsx)
- Text files (.txt)

Expected data structure:
- First column: Time values
- Remaining columns: Wavelength measurements
- Column headers should contain wavelength values

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