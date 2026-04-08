# Software Documentation

**Project:** SpecMap - Hyperspectral Data Analysis Tool  
**Version:** 1.0  
**Last Updated:** November 28, 2025

---

## Overview

This directory contains comprehensive technical documentation for the SpecMap software architecture, focusing on program structure, GUI hierarchy, error handling, and cleanup lifecycle.

---

## Documentation Files

### 1. [PROGRAM_STRUCTURE.md](PROGRAM_STRUCTURE.md)

**Purpose:** Complete hierarchical documentation of the SpecMap program structure starting from `main9.py`

**Contents:**
- Full program structure tree from entry point to leaf components
- Module hierarchy and dependencies
- Class instantiation flow with creation order
- Error propagation paths (bottom-up)
- Module dependency graph
- Data flow for loading and saving operations

**Use Cases:**
- Understanding overall code architecture
- Tracing execution flow from main entry
- Identifying where classes are instantiated
- Understanding module dependencies and import relationships
- Debugging module loading issues
- Planning refactoring efforts

---

### 2. [GUI_HIERARCHY_AND_LIFECYCLE.md](GUI_HIERARCHY_AND_LIFECYCLE.md)

**Purpose:** Detailed documentation of Tkinter GUI hierarchy, focusing on error handling directions and cleanup lifecycle

**Contents:**
- Complete GUI hierarchy tree with parent-child relationships
- Root instance (`tk.Tk`) propagation through components
- Error handling flow (directional: child → parent → root)
- Cleanup & closing flow (directional: root → parent → child)
- Potential error scenarios with mitigation strategies
- Best practices and recommended improvements

**Use Cases:**
- Understanding GUI widget ownership
- Debugging GUI-related errors (TclError, widget destruction)
- Implementing proper cleanup for new components
- Troubleshooting memory leaks
- Understanding error propagation direction
- Planning GUI refactoring

---

## Key Concepts

### Program Structure (main9.py)

```
main9.py (Entry)
    ↓
FileProcessorApp (Main application class)
    ↓
Component Classes (XYMap, Exportframe, TCSPCprocessor, etc.)
    ↓
Utility Classes (SpectrumData, Roihandler, PMclass)
    ↓
Library Functions (deflib, mathlib, etc.)
```

### GUI Hierarchy (tk.Tk root)

```
root (tk.Tk)
    ↓
notebook (ttk.Notebook)
    ↓
nodeframes (ttk.Frame × 7)
    ↓
Component frames (tk.Frame - passed to classes)
    ↓
Widgets (Button, Entry, Combobox, etc.)
```

### Error Flow Direction

```
Widget Error
    ↓ propagates upward
Parent Frame
    ↓ propagates upward
Component Class
    ↓ propagates upward
FileProcessorApp
    ↓ propagates upward
Root Window (handled by pressclose)
```

### Cleanup Flow Direction

```
User clicks [X]
    ↓
pressclose() called
    ↓ destroys downward
root.destroy()
    ↓ automatic cascade
notebook destroyed
    ↓ automatic cascade
All child widgets destroyed
```

---

## Documentation Standards

### Graphical Representations

Both documents use ASCII art for visual representation:

- **Tree structures:** Use `├──`, `└──`, `│` for hierarchy
- **Flow charts:** Use `┌──┐`, `│`, `└──┘`, `▼`, `▶` for direction
- **Boxes:** Use Unicode box drawing characters for emphasis
- **Arrows:** Use `→`, `↓`, `▲`, `▶` to show flow direction

### Directional Analysis

1. **Error Propagation:** ⬆ UPWARD (Child → Parent → Root)
   - Errors bubble up from low-level components to high-level handlers
   
2. **Cleanup Flow:** ⬇ DOWNWARD (Root → Parent → Child)
   - Destruction cascades from root window to leaf widgets

3. **Data Flow:** Documented separately for each operation
   - Loading: Entry point → Processing → Storage
   - Saving: Retrieval → Serialization → File

---

## How to Use This Documentation

### For New Developers

1. **Start here:** Read this README
2. **Understand structure:** Read [PROGRAM_STRUCTURE.md](PROGRAM_STRUCTURE.md) sections 1-3
3. **Learn GUI flow:** Read [GUI_HIERARCHY_AND_LIFECYCLE.md](GUI_HIERARCHY_AND_LIFECYCLE.md) sections 1-2
4. **Study examples:** Look at code with documentation side-by-side

### For Debugging

1. **GUI errors (TclError):**
   - Check [GUI_HIERARCHY_AND_LIFECYCLE.md](GUI_HIERARCHY_AND_LIFECYCLE.md) Section 5: Potential Error Scenarios
   - Verify widget parent-child relationships in Section 1

2. **Import errors:**
   - Check [PROGRAM_STRUCTURE.md](PROGRAM_STRUCTURE.md) Section 5: Module Dependencies
   - Verify import order matches dependency graph

3. **Memory leaks:**
   - Check [GUI_HIERARCHY_AND_LIFECYCLE.md](GUI_HIERARCHY_AND_LIFECYCLE.md) Section 4: Cleanup Flow
   - Verify cleanup methods are called properly

4. **Data loading errors:**
   - Check [PROGRAM_STRUCTURE.md](PROGRAM_STRUCTURE.md) Section 4: Error Propagation Paths
   - Trace error handling from SpectrumData → XYMap → FileProcessorApp

### For Adding Features

1. **New GUI component:**
   - Review [GUI_HIERARCHY_AND_LIFECYCLE.md](GUI_HIERARCHY_AND_LIFECYCLE.md) Section 2: Root Propagation
   - Follow pattern: receive parent frame as parameter
   - Implement cleanup method (on_close)

2. **New data processing:**
   - Review [PROGRAM_STRUCTURE.md](PROGRAM_STRUCTURE.md) Section 3: Class Instantiation Flow
   - Add to appropriate level in hierarchy
   - Implement error handling following existing patterns

3. **New module:**
   - Review [PROGRAM_STRUCTURE.md](PROGRAM_STRUCTURE.md) Section 5: Module Dependencies
   - Ensure no circular dependencies
   - Import only necessary dependencies

---

## Quick Reference Tables

### Component Ownership

| Component | Owner | Parent Frame | Cleanup Method |
|-----------|-------|--------------|----------------|
| menu_bar | FileProcessorApp | root | Automatic |
| notebook | FileProcessorApp | root | Automatic |
| nodeframes | FileProcessorApp | notebook | Automatic |
| cmapframe | FileProcessorApp | nodeframes['Hyperspectra'] | Manual (.destroy()) |
| specframe | FileProcessorApp | nodeframes['Hyperspectra'] | Manual (.destroy()) |
| Nanomap | FileProcessorApp | Uses cmapframe/specframe | Manual (.on_close()) |
| Exporter | FileProcessorApp | nodeframes['HSI Plot'] | Automatic |
| TCSPC_Processor | FileProcessorApp | nodeframes['TCSPC'] | Automatic |

### Error Handling Levels

| Level | Component | Error Detection | Notification | Propagation |
|-------|-----------|----------------|--------------|-------------|
| 0 | Root Window | Protocol handler | None | Application exit |
| 1 | FileProcessorApp | try/except + validation | messagebox | Stops here |
| 2 | XYMap | try/except + traceback | Console | Return False |
| 3 | SpectrumData | Flag-based | None | Flag check |
| 4 | Roihandler | Validation checks | matplotlib | Upward |
| 5 | Component Classes | try/except | Console/None | Varies |

### Cleanup Sequence

| Stage | Component | Action | Triggered By |
|-------|-----------|--------|--------------|
| 1 | Threads | Set daemon | pressclose() |
| 2 | Root | destroy() | pressclose() |
| 3-6 | All widgets | Auto-destroy | Tkinter cascade |
| 7 | FileProcessorApp | on_closing() | pressclose() |
| Manual | XYMap | on_close() | spec_loadfiles() |
| Manual | Roihandler | on_close() | XYMap.on_close() |

---

## Maintenance

### Updating Documentation

When modifying the codebase:

1. **New class added:** Update both documents
   - Add to program structure tree
   - Add to GUI hierarchy if it creates widgets
   - Document cleanup requirements

2. **New frame created:** Update GUI_HIERARCHY_AND_LIFECYCLE.md
   - Add to hierarchy tree
   - Document parent-child relationship
   - Note cleanup behavior

3. **Error handling changed:** Update error propagation sections
   - Document new error types
   - Update error handling strategy
   - Add to error scenarios if critical

4. **Module dependency changed:** Update PROGRAM_STRUCTURE.md
   - Update import graph
   - Check for circular dependencies
   - Update module hierarchy

### Documentation Review Checklist

- [ ] All new classes documented in program structure
- [ ] All new frames documented in GUI hierarchy
- [ ] Error handling paths updated
- [ ] Cleanup methods documented
- [ ] Module dependencies verified
- [ ] Examples updated if needed
- [ ] Version history updated

---

## Contributing

When contributing to SpecMap:

1. **Read both documentation files** before making significant changes
2. **Follow existing patterns** for GUI component creation
3. **Implement proper cleanup** for all resources
4. **Document changes** in this documentation
5. **Test cleanup behavior** by repeatedly loading/unloading data

---

## Additional Resources

- **Main README:** [../README.md](../README.md) - User-facing documentation
- **Project Structure:** [../PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - High-level overview
- **Project TODO:** [../PROJECT_TODO.md](../PROJECT_TODO.md) - Task tracking

todo: add a branch for elias


---

## Contact

For questions about this documentation:
- Check inline code comments in `main9.py` and `lib9.py`
- Review error handling examples in the code
- Consult the git commit history for context

---

**Last Updated:** November 28, 2025  
**Maintainer:** PyProgMo  
**Documentation Version:** 1.0
