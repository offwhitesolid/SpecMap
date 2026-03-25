# SpecMap Project TODO List

**Project**: SpecMap - Hyperspectral Data Analysis Tool  
**Last Updated**: November 28, 2025  
**Repository**: PyProgMo/SpecMap

---

## Legend
- **DONE**: Task completed
- 🔄 **IN PROGRESS**: Currently being worked on
- ⏸️ **BLOCKED**: Waiting on dependencies or external factors
- 📋 **TODO**: Not yet started
- **CANCELLED**: Task no longer needed

**Assignees**:
- 👤 **User**: Project owner/developer
- 🤖 **Copilot**: AI assistant
- 👥 **Team**: Multiple contributors

---

## 1. Core Functionality & Bug Fixes

### 1.1 Data Loading & Processing
- [ ] 📋 **Test load/save functionality with real datasets** - 👤 User
  - Verify XYMap save_state() and load_state() work correctly
  - Test with various dataset sizes
  - Validate metadata preservation
  
- [ ] 📋 **Add progress bar for large file loading** - 🤖 Copilot
  - Implement progress tracking in loadfiles()
  - Add GUI progress indicator
  - Estimated time: 2-3 hours

- [ ] 📋 **Handle corrupted/malformed data files gracefully** - 🤖 Copilot
  - Add try-except blocks with informative error messages
  - Implement file validation before loading
  - Log errors to file for debugging

### 1.2 GUI Improvements
- [x] **Build GUI even when no data is loaded** - 🤖 Copilot
  - Modified build_button_frame() to construct full GUI
  - Added disabled states for data-dependent buttons
  - Completed: November 28, 2025

- [ ] 📋 **Add keyboard shortcuts for common operations** - 🤖 Copilot
  - Ctrl+O: Open file
  - Ctrl+S: Save data
  - Ctrl+E: Export data
  - Space: Toggle plot view

- [ ] 📋 **Implement undo/redo functionality** - 🤖 Copilot
  - Store operation history
  - Add undo/redo buttons to GUI
  - Limit history depth to conserve memory

- [ ] 📋 **Add dark mode theme option** - 👥 Team
  - Create theme configuration
  - Apply consistent styling across all frames
  - Save theme preference in defaults

### 1.3 Performance Optimization
- [ ] 📋 **Profile and optimize loadfiles() for large datasets** - 🤖 Copilot
  - Use cProfile to identify bottlenecks
  - Optimize file I/O operations
  - Consider memory-mapped files for very large datasets

- [ ] 📋 **Implement lazy loading for spectral data** - 🤖 Copilot
  - Load spectrum metadata first
  - Load full spectrum data on-demand
  - Cache frequently accessed spectra

- [ ] 📋 **Optimize cosmic removal algorithms** - 🤖 Copilot
  - Vectorize remaining operations
  - Use numba JIT compilation for hotspots
  - Benchmark all methods

---

## 2. Cosmic Ray Removal Enhancements

### 2.1 Algorithm Development
- [x] **Implement Combined Linear-Neighbor method** - 🤖 Copilot
  - Created two-stage algorithm
  - Added to cosmicfuncts dictionary
  - Completed: November 28, 2025

- [x] **Document Combined Linear-Neighbor method** - 🤖 Copilot
  - Added mathematical documentation
  - Updated performance comparison tables
  - Updated use case recommendations
  - Completed: November 28, 2025

- [ ] 📋 **Add visual comparison tool for cosmic removal methods** - 🤖 Copilot
  - Create side-by-side before/after plots
  - Show residual difference maps
  - Allow interactive method selection

- [ ] 📋 **Implement automated parameter optimization** - 🤖 Copilot
  - Use cross-validation to find optimal thresh/width
  - Create parameter suggestion wizard
  - Store optimal parameters per dataset type

### 2.2 Matrix Methods
- [ ] 📋 **Create Matrix version of Combined Linear-Neighbor** - 🤖 Copilot
  - Adapt algorithm for 2D spatial correlation
  - Add to correlationcosmicfuncts dictionary
  - Test on real hyperspectral datasets

- [ ] 📋 **Benchmark all Matrix methods on test datasets** - 👤 User
  - Compare accuracy metrics
  - Measure execution time
  - Document results in COSMIC_REMOVAL_METHODS.md

---

## 3. Testing & Quality Assurance

### 3.1 Unit Tests
- [ ] 📋 **Create unit test suite for deflib1.py** - 🤖 Copilot
  - Test all cosmic removal functions
  - Test utility functions
  - Test configuration loading/saving
  - Framework: pytest

- [ ] 📋 **Create unit test suite for mathlib3.py** - 🤖 Copilot
  - Test all fitting functions
  - Validate parameter extraction
  - Test edge cases
  - Target coverage: >80%

- [ ] 📋 **Create unit test suite for PMclasslib1.py** - 🤖 Copilot
  - Test SpectrumData class
  - Test PMclass functionality
  - Test data serialization

### 3.2 Integration Tests
- [ ] 📋 **Test complete workflow: load → process → fit → export** - 👤 User
  - Use sample datasets from testdatasets/
  - Verify output correctness
  - Document expected vs actual results

- [ ] 📋 **Test save/load state with various data types** - 👤 User
  - Test with ROI masks
  - Test with fit results
  - Test with multiple HSI images

### 3.3 User Acceptance Testing
- [ ] 📋 **Create user testing scenarios** - 👤 User
  - Document common workflows
  - Create test data packages
  - Collect user feedback

---

## 4. Documentation Improvements

### 4.1 User Documentation
- [ ] 📋 **Create video tutorials** - 👤 User
  - Getting started tutorial
  - Advanced features demonstration
  - Troubleshooting common issues

- [ ] 📋 **Add more screenshots to README.md** - 👤 User
  - Main interface overview
  - Example plots and colormaps
  - Step-by-step workflow images

- [ ] 📋 **Create FAQ section** - 🤖 Copilot
  - Common errors and solutions
  - Performance tips
  - File format questions

### 4.2 Developer Documentation
- [x] **Create software architecture documentation** - 🤖 Copilot
  - Created Software_Documentation folder
  - PROGRAM_STRUCTURE.md - Complete program tree from main9.py
  - GUI_HIERARCHY_AND_LIFECYCLE.md - Tkinter hierarchy with error/cleanup flows
  - Graphical ASCII representations for visual clarity
  - Completed: November 28, 2025

- [ ] 📋 **Add inline code documentation** - 🤖 Copilot
  - Add docstrings to all functions
  - Document complex algorithms
  - Add type hints throughout

- [ ] 📋 **Create API reference documentation** - 🤖 Copilot
  - Use Sphinx to generate docs
  - Document all public methods
  - Include usage examples

- [ ] 📋 **Document data file formats** - 👤 User
  - Specify expected file structure
  - Document metadata fields
  - Provide file format conversion utilities

---

## 5. New Features

### 5.1 Data Analysis Features
- [ ] 📋 **Add spectral unmixing capabilities** - 🤖 Copilot
  - Implement NMF/PCA decomposition
  - Create interactive component viewer
  - Export component spectra

- [ ] 📋 **Implement automated peak detection** - 🤖 Copilot
  - Use scipy.signal.find_peaks
  - Add peak annotation to plots
  - Export peak positions and intensities

- [ ] 📋 **Add batch processing mode** - 🤖 Copilot
  - Process multiple datasets without GUI
  - Command-line interface
  - Generate automated reports

### 5.2 Visualization Features
- [ ] 📋 **Add 3D visualization option** - 👥 Team
  - Use plotly or mayavi
  - Interactive rotation and zoom
  - Export 3D plots

- [ ] 📋 **Implement custom colormap editor** - 🤖 Copilot
  - Visual colormap designer
  - Save custom colormaps
  - Share colormaps between users

- [ ] 📋 **Add spectrum overlay comparison tool** - 🤖 Copilot
  - Compare multiple spectra on one plot
  - Calculate difference spectra
  - Statistical comparison metrics

### 5.3 Export Features
- [ ] 📋 **Add export to HDF5 format** - 🤖 Copilot
  - More efficient for large datasets
  - Preserve full metadata
  - Maintain data hierarchy

- [ ] 📋 **Create publication-ready figure export** - 🤖 Copilot
  - High-resolution PNG/PDF export
  - Adjustable DPI settings
  - Batch export all figures

- [ ] 📋 **Add Excel export with formatting** - 🤖 Copilot
  - Use openpyxl for formatting
  - Create summary sheets
  - Include embedded plots

---

## 6. Code Quality & Maintenance

### 6.1 Refactoring
- [ ] 📋 **Refactor lib9.py - split into smaller modules** - 🤖 Copilot
  - lib9_spectrum.py: SpectrumData class
  - lib9_xymap.py: XYMap class
  - lib9_roi.py: ROI handling
  - lib9_plotting.py: Plotting functions

- [ ] 📋 **Remove deprecated functions** - 🤖 Copilot
  - Review all commented-out code
  - Remove unused imports
  - Clean up oldfiles/ directory

- [ ] 📋 **Standardize naming conventions** - 🤖 Copilot
  - Use snake_case consistently
  - Rename cryptic variable names
  - Update documentation accordingly

### 6.2 Dependencies
- [ ] 📋 **Update to latest package versions** - 👤 User
  - Test compatibility with new versions
  - Update requirements.txt
  - Fix any breaking changes

- [ ] 📋 **Remove unused dependencies** - 🤖 Copilot
  - Audit all imports
  - Update requirements.txt
  - Reduce installation size

### 6.3 Error Handling
- [ ] 📋 **Implement centralized error logging** - 🤖 Copilot
  - Use Python logging module
  - Create rotating log files
  - Add log viewer in GUI

- [ ] 📋 **Add comprehensive error messages** - 🤖 Copilot
  - User-friendly error dialogs
  - Actionable suggestions
  - Link to relevant documentation

---

## 7. Deployment & Distribution

### 7.1 Packaging
- [ ] 📋 **Create PyPI package** - 👤 User
  - Setup.py configuration
  - Upload to PyPI
  - Versioning strategy

- [ ] 📋 **Create standalone executable** - 🤖 Copilot
  - Use PyInstaller or cx_Freeze
  - Bundle all dependencies
  - Test on clean Windows/Linux systems

- [ ] 📋 **Create Docker container** - 👥 Team
  - Dockerfile with all dependencies
  - Docker Compose for easy setup
  - Document container usage

### 7.2 Version Control
- [ ] 📋 **Set up automated testing with GitHub Actions** - 👥 Team
  - Run tests on every commit
  - Test on multiple Python versions
  - Generate coverage reports

- [ ] 📋 **Create release workflow** - 👤 User
  - Automated version bumping
  - Changelog generation
  - Tagged releases

### 7.3 User Support
- [ ] 📋 **Create issue templates** - 🤖 Copilot
  - Bug report template
  - Feature request template
  - Question template

- [ ] 📋 **Set up discussions forum** - 👤 User
  - Enable GitHub Discussions
  - Create discussion categories
  - Pin FAQ and resources

---

## 8. Research & Exploration

### 8.1 New Algorithms
- [ ] 📋 **Research machine learning for cosmic detection** - 👥 Team
  - Literature review
  - Train CNN on labeled data
  - Compare with traditional methods

- [ ] 📋 **Explore GPU acceleration** - 🤖 Copilot
  - CuPy for GPU NumPy operations
  - CUDA kernels for critical functions
  - Benchmark speedup

### 8.2 Integration
- [ ] 📋 **Add Igor Pro export compatibility** - 👤 User
  - Generate .ibw files
  - Maintain metadata compatibility
  - Test with Igor Program/ files

- [ ] 📋 **Create Jupyter notebook integration** - 🤖 Copilot
  - IPython widgets for interactive analysis
  - Example notebooks in openerJN/
  - Documentation for notebook usage

---

## 9. Specific Issues & Bugs

### 9.1 Known Issues
- [ ] 📋 **Fix type checking warnings in deflib1.py** - 🤖 Copilot
  - Address "is not a known attribute of None" warnings
  - Add proper type annotations
  - Use Optional[] where appropriate

- [ ] 📋 **Fix sticky parameter in grid - should be string not tuple** - 🤖 Copilot
  - Search for all grid(..., sticky=tuple) calls
  - Replace with string format (e.g., 'we')
  - Test layout behavior

- [ ] 📋 **Fix spine visibility method calls** - 🤖 Copilot
  - Replace spine() calls with .set_visible()
  - Update plot_HSI function
  - Update any other plotting functions

### 9.2 Performance Issues
- [ ] 📋 **Investigate slow fitting on large datasets** - 👤 User
  - Profile fittoMatrixfitparams()
  - Optimize scipy.optimize calls
  - Consider parallel processing

---

## 10. Project Management

### 10.1 Milestones
- [ ] 📋 **Version 1.0 Release** - 👤 User
  - All critical bugs fixed
  - Core features complete
  - Documentation complete
  - Target date: TBD

- [ ] 📋 **Version 2.0 Release** - 👤 User
  - Machine learning features
  - GPU acceleration
  - Web interface option
  - Target date: TBD

### 10.2 Communication
- [ ] 📋 **Create project roadmap** - 👤 User
  - Public roadmap on GitHub
  - Feature voting system
  - Regular status updates

---

## Priority Matrix

### High Priority (Do First)
1. Fix type checking warnings (9.1)
2. Test save/load functionality (1.1)
3. Unit test suite creation (3.1)
4. Documentation improvements (4.1, 4.2)

### Medium Priority (Do Next)
1. Performance optimization (1.3)
2. GUI improvements (1.2)
3. New visualization features (5.2)
4. Code refactoring (6.1)

### Low Priority (Nice to Have)
1. Dark mode theme (1.2)
2. 3D visualization (5.2)
3. Docker container (7.1)
4. Machine learning exploration (8.1)

---

## Notes

### Recent Completions
- **November 28, 2025**: Implemented and documented Combined Linear-Neighbor cosmic removal method
- **November 28, 2025**: Refactored GUI to build even without data loaded

### Blockers
- None currently

### Questions for User
1. What is the priority for Version 1.0 release?
2. Are there specific datasets that need special handling?
3. Which new features are most important for your research?

---

**Next Review Date**: December 5, 2025  
**Responsible for Review**: 👤 User

---

## How to Use This TODO List

1. **For Copilot Tasks**: When starting a task marked with 🤖 Copilot, change status to 🔄 IN PROGRESS
2. **When Completing Tasks**: Change checkbox to [x] and emoji to ✅, add completion date
3. **For Blocked Tasks**: Change to ⏸️ BLOCKED and explain reason in Notes section
4. **For Cancelled Tasks**: Change to CANCELLED and explain reason
5. **Adding New Tasks**: Add to appropriate section with assignee and priority
6. **Regular Updates**: Review and update status weekly

---

*This is a living document. Update it frequently as the project evolves.*
