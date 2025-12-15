# SpecMap Project Structure

## Overview
This document describes the architecture and file organization of the SpecMap hyperspectral data analysis application.

## Directory Structure

```
SpecMap1/
├── 📄 main9.py                   # Main application entry point
├── 📄 lib9.py                    # Core hyperspectral analysis engine
├── 📄 deflib1.py                 # Default settings and utility functions
├── 📄 claralib1.py               # Clara image processing module
├── 📄 mathlib3.py                # Mathematical fitting functions
├── 📄 PMclasslib1.py             # Pixel matrix and spectra data classes
├── 📄 newtonspeclib1.py          # Newton spectrum analysis framework
├── 📄 export1.py                 # Data export functionality
├── 📄 defaults.txt               # Configuration file with default values
├── 📄 requirements.txt           # Python package dependencies
├── 📄 README.md                  # Complete project documentation
├── 📄 PROJECT_STRUCTURE.md       # This file - project architecture
├── 📄 COSMIC_REMOVAL_METHODS.md  # Mathematical documentation of all methods
├── 📄 .copilotignore             # Files excluded from AI analysis
├── 📄 LICENSE                    # Project license
└── 📁 Directories/
    ├── 📁 __pycache__/           # Python bytecode cache (ignored)
    ├── 📁 exported Pixelmatrix/  # Output directory for exported data
    ├── 📁 hsidata/               # Sample hyperspectral data files
    ├── 📁 savefiles/             # Saved analysis sessions
    ├── 📁 Igor Program/          # External Igor Pro integration files
    ├── 📁 openspec/              # Spectrum opening utilities
    ├── 📁 openerJN/              # Jupyter notebook examples
    ├── 📁 pythontestsrc/         # Test scripts and examples
    ├── 📁 scaleimages/           # Image scaling utilities
    ├── 📁 testdatasets/          # Sample datasets for testing
    ├── 📁 oldfiles/              # Legacy/backup files
    └── 📁 standalone/            # Standalone utility scripts
```

## Core Architecture

### Application Layer
- **`main9.py`**: Application entry point and GUI controller
  - Manages the main Tkinter interface
  - Coordinates between different modules
  - Handles file loading workflows
  - Manages application lifecycle

### Data Processing Layer
- **`lib9.py`**: Core hyperspectral analysis engine
  - `SpectrumData`: Individual spectrum container
  - `XYMap`: Main hyperspectral dataset manager
  - `Roihandler`: Region of interest management
  - Interactive plotting and analysis

### Utility Layer
- **`deflib1.py`**: Configuration and utility functions
  - Default settings management
  - Cosmic ray removal algorithms
  - File dialog utilities
  - Configuration persistence

### Mathematical Layer
- **`mathlib3.py`**: Scientific computation functions
  - Spectral fitting models (Gaussian, Lorentzian, Voigt)
  - Parameter estimation algorithms
  - Peak detection and analysis
  - Mathematical utilities

### Specialized Processing
- **`claralib1.py`**: Clara imaging analysis
  - 2D Gaussian fitting for beam characterization
  - Multi-magnification support
  - Area calculations

- **`PMclasslib1.py`**: Data structure definitions
  - Pixel matrix containers
  - Spectrum data classes
  - Metadata management

- **`export1.py`**: Data export functionality
  - CSV export with metadata
  - File format conversion
  - Data serialization

- **`newtonspeclib1.py`**: Newton spectrum framework
  - Framework for Newton-specific analysis
  - Extensible for future features

## Data Flow Architecture

```
📂 Input Data Files
    ↓
🔄 File Loading (main9.py)
    ↓
📊 SpectrumData Objects (lib9.py)
    ↓
🗂️ XYMap Organization
    ↓
⚙️ Processing Pipeline
    ├── Background Correction (deflib1.py)
    ├── Cosmic Ray Removal (deflib1.py)
    └── Power Correction (lib9.py)
    ↓
📈 Interactive Analysis
    ├── Pixel Selection (lib9.py)
    ├── Spectral Fitting (mathlib3.py)
    ├── ROI Analysis (lib9.py)
    └── Clara Processing (claralib1.py)
    ↓
💾 Export Results (export1.py)
```

## Module Dependencies

### Core Dependencies
- **Tkinter**: GUI framework
- **Matplotlib**: Plotting and visualization
- **NumPy**: Numerical computations
- **SciPy**: Scientific computing and curve fitting
- **PIL/Pillow**: Image processing

### Internal Dependencies
```
main9.py
├── lib9.py (core engine)
├── deflib1.py (utilities)
├── claralib1.py (imaging)
├── export1.py (export)
└── newtonspeclib1.py (newton)

lib9.py
├── mathlib3.py (fitting functions)
├── PMclasslib1.py (data structures)
└── deflib1.py (utilities)

claralib1.py
└── deflib1.py (image loading)
```

## Configuration System

### Settings Management
- **`defaults.txt`**: Persistent configuration storage
- **`deflib1.py`**: Configuration loading and validation
- Type-safe configuration with fallback defaults
- Runtime configuration updates

### Key Configuration Areas
- File paths and data directories
- Processing parameters (cosmic removal, background correction)
- Display preferences (fonts, window sizes, colormaps)
- Analysis settings (wavelength ranges, fitting constraints)

## Extension Points

### Adding New Analysis Methods
1. **Mathematical Models**: Extend `mathlib3.py` with new fitting functions
2. **Processing Algorithms**: Add new methods to `deflib1.py`
3. **Visualization**: Extend plotting capabilities in `lib9.py`

### Adding New Data Formats
1. **File Parsers**: Extend loading functions in `lib9.py`
2. **Data Structures**: Add new classes to `PMclasslib1.py`
3. **Export Formats**: Extend `export1.py` with new output formats

### GUI Extensions
1. **New Tabs**: Add notebook pages in `main9.py`
2. **Custom Widgets**: Create specialized GUI components
3. **Menu Items**: Extend the menu system in `deflib1.py`

## Development Workflow

### Code Organization Principles
- **Separation of Concerns**: Each module has a specific responsibility
- **Modularity**: Loosely coupled, highly cohesive components
- **Configuration-Driven**: Behavior controlled through settings
- **Extensibility**: Clean interfaces for adding new features

### Best Practices
- Follow existing naming conventions
- Maintain comprehensive error handling
- Document all public interfaces
- Use type hints where appropriate
- Test new features thoroughly

## Performance Considerations

### Memory Management
- Efficient NumPy array operations
- On-demand data loading
- Automatic cleanup of matplotlib figures

### Computational Efficiency
- Vectorized operations for spectral processing
- Optimized fitting algorithms
- Caching of computed results

### GUI Responsiveness
- Background processing for long operations
- Progress indicators for user feedback
- Non-blocking file operations

This structure provides a solid foundation for understanding, maintaining, and extending the SpecMap hyperspectral analysis application.