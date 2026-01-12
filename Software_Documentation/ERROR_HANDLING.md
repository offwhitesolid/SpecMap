# ErrorEngine - Centralized Error Handling and Logging

**Module:** `error_engine.py`  
**Version:** 1.0  
**Last Updated:** January 12, 2026

---

## Overview

The ErrorEngine provides a unified error handling and logging system for the SpecMap application. It captures exceptions with full context, logs them with detailed information, and displays user-friendly error messages when appropriate.

---

## Features

### 1. Centralized Logging
- **Rotating File Handler**: Max 5MB per log file, keeps 5 backup files
- **Log Directory**: `logs/` (automatically created)
- **Log Format**: `[timestamp] [level] [module:function:line] - message`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Thread-Safe**: Safe for concurrent operations (e.g., ThreadPoolExecutor in XYMap)

### 2. Context Tracking
For each error, the following information is captured:
- Exception type and message
- Full stack trace
- Current file/path being processed (if applicable)
- User action that triggered the error
- Application state information
- Timestamp

### 3. User-Friendly Messages
- Automatic messagebox display for critical errors
- Context-aware error messages
- Helpful hints based on error type
- Option to suppress messageboxes for batch operations

### 4. Multiple Usage Patterns
- Context manager (recommended for file operations)
- Decorator (for entire functions)
- Direct method calls (for existing try/except blocks)
- Simple logging methods (info, warning, debug)

---

## Installation & Configuration

### Initialization in main9.py

```python
import error_engine as ee

if __name__ == "__main__":
    # Initialize error engine and logging
    logger = ee.setup_logger("SpecMap", "logs")
    error_engine = ee.initialize_error_engine(logger, show_messagebox=True)
    logger.info("SpecMap Application Starting")
    
    # Rest of application startup...
```

### Accessing ErrorEngine in Classes

```python
class FileProcessorApp:
    def __init__(self, root, defaults):
        # Get error engine instance
        try:
            self.error_engine = ee.get_error_engine()
        except RuntimeError:
            # Fallback if not initialized
            logger = ee.setup_logger("SpecMap", "logs")
            self.error_engine = ee.initialize_error_engine(logger)
```

---

## Usage Patterns

### Pattern 1: Context Manager (Recommended for File Operations)

**Best for:** File I/O operations, data loading, resource management

```python
# Example: Loading a spectrum file
with error_engine.context("Loading spectrum file", filename=path):
    data = load_spectrum(path)

# Example: Saving HSI data
with error_engine.context("Saving HSI data", filename=filename):
    self.Nanomap.save_state(filename)

# Example: Processing multiple files
for folder in folders:
    with error_engine.context("Processing folder", folder=folder):
        process_folder(folder)
```

**Advantages:**
- Automatic error handling on context exit
- Clean syntax
- Captures context information automatically
- No need for explicit try/except

---

### Pattern 2: Decorator (Recommended for Functions)

**Best for:** Entire function error handling

```python
@error_engine.track_errors(action="File save operation")
def save_file(self, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)

@error_engine.track_errors(action="Loading spectrum files")
def loadfiles(self):
    for fname in self.fnames:
        spec = SpectrumData(fname, self.WL, self.BG)
        self.specs.append(spec)
```

**Advantages:**
- Function-level error tracking
- Automatic context from function name
- Minimal code changes
- Handles all exceptions in function

---

### Pattern 3: Direct Exception Handling (Existing Code)

**Best for:** Integrating with existing try/except blocks

```python
try:
    result = risky_operation()
except FileNotFoundError as e:
    self.error_engine.handle_exception(
        e,
        context="Loading spectrum file",
        additional_info={"filename": path, "user_action": "Load button clicked"}
    )
except Exception as e:
    self.error_engine.handle_exception(
        e,
        context="Processing data",
        severity="ERROR",
        show_user_message=True
    )
```

**Advantages:**
- Fine-grained control
- Can handle different exception types differently
- Compatible with existing error handling
- Can suppress user messages for batch operations

---

### Pattern 4: Simple Logging

**Best for:** Informational messages, warnings, debug output

```python
# Info logging
error_engine.log_info("HSI data loaded successfully", 
                     filename=filename,
                     num_spectra=len(self.specs))

# Warning logging
error_engine.log_warning("Missing optional metadata", 
                        field="magnification",
                        file=filename)

# Debug logging
error_engine.log_debug("WL axis read successfully", 
                      num_points=len(self.WL))
```

---

## Integration Examples

### main9.py - FileProcessorApp

#### init_spec_loadfiles()
```python
def init_spec_loadfiles(self):
    if self.make_multiple_HSIsbool.get() == True:
        filemaindir = self.multiple_HSIs_dir_entry.get()
        savedir = self.multiple_HSIs_save_dir_entry.get()
        
        try:
            if not os.path.exists(filemaindir):
                raise FileNotFoundError(f"Main directory not found: {filemaindir}")
            
            # Process each folder
            for folder in foldersinmaindir:
                try:
                    self.spec_loadfiles()
                except Exception as e:
                    self.error_engine.handle_exception(
                        e,
                        context=f"Processing folder: {fullfolderpath}",
                        show_user_message=False,  # Don't show dialog for each error in batch
                        additional_info={
                            "folder": fullfolderpath,
                            "user_action": "Batch HSI processing"
                        }
                    )
                    continue
        except Exception as e:
            self.error_engine.handle_exception(
                e,
                context="Loading multiple HSI directories",
                additional_info={
                    "main_directory": filemaindir,
                    "user_action": "Load HSI data button clicked"
                }
            )
```

#### saveNanomap()
```python
def saveNanomap(self, filename):
    try:
        if not filename:
            self.error_engine.log_warning("No filename provided", user_action="Save HSI data")
            return
        
        self.error_engine.log_info("Saving HSI data", filename=filename)
        success = self.Nanomap.save_state(filename)
        
        if success:
            messagebox.showinfo("Success", f"Data saved successfully to:\n{filename}")
            self.error_engine.log_info("HSI data saved successfully", filename=filename)
        else:
            raise Exception("save_state returned False")
            
    except Exception as e:
        self.error_engine.handle_exception(
            e,
            context="Saving HSI data",
            additional_info={"filename": filename, "user_action": "Save button clicked"}
        )
        messagebox.showerror("Error", "Failed to save data. Check console for details.")
```

#### loadhsisaved()
```python
def loadhsisaved(self, filename):
    try:
        if not os.path.exists(filename):
            self.error_engine.log_warning("File not found", filename=filename)
            messagebox.showerror("Error", f"File not found:\n{filename}")
            return
        
        self.error_engine.log_info("Loading saved HSI data", filename=filename)
        success = self.Nanomap.load_state(filename)
        
        if success:
            messagebox.showinfo("Success", f"Data loaded successfully")
            self.error_engine.log_info("HSI data loaded successfully", filename=filename)
    except Exception as e:
        self.error_engine.handle_exception(
            e,
            context="Loading saved HSI data",
            additional_info={"filename": filename}
        )
```

---

### lib9.py - Core Classes

#### SpectrumData._read_file()
```python
def _read_file(self):
    try:
        error_engine = ee.get_error_engine()
        
        with open(self.filename, 'r') as file:
            lines = file.readlines()
        
        # Process file...
        
    except FileNotFoundError as e:
        print("Error: File not found -", self.filename)
        try:
            error_engine = ee.get_error_engine()
            error_engine.handle_exception(
                e,
                context="Reading spectrum file",
                show_user_message=False,
                additional_info={"filename": self.filename}
            )
        except:
            pass
        raise
```

#### XYMap.loadfiles()
```python
def loadfiles(self):
    try:
        error_engine = ee.get_error_engine()
        error_engine.log_info(f"Loading {len(self.fnames)} spectrum files")
        
        # Load files...
        
    except Exception as e:
        try:
            error_engine = ee.get_error_engine()
            error_engine.handle_exception(
                e,
                context="Loading spectrum files",
                show_user_message=False,
                additional_info={"num_files": len(self.fnames)}
            )
        except:
            pass
        raise
```

#### XYMap.save_state()
```python
def save_state(self, filename):
    try:
        error_engine = ee.get_error_engine()
        error_engine.log_info("Saving XYMap state", filename=filename)
        
        # Save state...
        
        error_engine.log_info("XYMap state saved successfully", 
                            filename=filename,
                            num_spectra=len(self.specs))
        return True
    except Exception as e:
        try:
            error_engine = ee.get_error_engine()
            error_engine.handle_exception(
                e,
                context="Saving XYMap state",
                show_user_message=False,
                additional_info={"filename": filename}
            )
        except:
            pass
        return False
```

---

## Log File Structure

### Location
```
SpecMap/
├── logs/
│   ├── specmap.log          # Current log file
│   ├── specmap.log.1        # Backup 1 (most recent)
│   ├── specmap.log.2        # Backup 2
│   ├── specmap.log.3        # Backup 3
│   ├── specmap.log.4        # Backup 4
│   └── specmap.log.5        # Backup 5 (oldest)
```

### Log Entry Format

```
[2026-01-12 10:30:45] [INFO] [main9:__main__:1125] - SpecMap Application Starting
[2026-01-12 10:30:46] [INFO] [lib9:loadfiles:2005] - Loading 144 spectrum files
[2026-01-12 10:31:02] [INFO] [lib9:save_state:2533] - Saving XYMap state [filename=/path/to/save.pkl]
[2026-01-12 10:31:05] [ERROR] [lib9:_read_file:167] - Context: Reading spectrum file
Context Stack: Loading spectrum files
Error Type: FileNotFoundError
Error Message: [Errno 2] No such file or directory: '/path/to/file.txt'
Additional Info: filename=/path/to/file.txt
Traceback:
File "/path/to/lib9.py", line 82, in _read_file
    with open(self.filename, 'r') as file:
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/file.txt'
```

---

## Best Practices

### 1. Use Context Managers for File Operations
```python
# Good
with error_engine.context("Loading file", filename=path):
    load_file(path)

# Avoid
try:
    load_file(path)
except Exception as e:
    error_engine.handle_exception(e, context="Loading file")
```

### 2. Suppress User Messages in Batch Operations
```python
for folder in folders:
    try:
        process_folder(folder)
    except Exception as e:
        error_engine.handle_exception(
            e,
            context=f"Processing {folder}",
            show_user_message=False  # Don't show dialog for each error
        )
```

### 3. Include Context Information
```python
# Good - includes helpful context
error_engine.handle_exception(
    e,
    context="Saving HSI data",
    additional_info={
        "filename": filename,
        "num_spectra": len(self.specs),
        "user_action": "Save button clicked"
    }
)

# Less helpful
error_engine.handle_exception(e, context="Error occurred")
```

### 4. Use Appropriate Log Levels
```python
error_engine.log_debug("WL axis: 1024 points")  # Verbose details
error_engine.log_info("Data loaded successfully")  # Normal operations
error_engine.log_warning("Missing optional field")  # Potential issues
# Errors are logged automatically via handle_exception()
```

### 5. Handle ErrorEngine Initialization Gracefully
```python
# Always check if error engine is available
try:
    error_engine = ee.get_error_engine()
    error_engine.log_info("Operation completed")
except RuntimeError:
    # ErrorEngine not initialized, fallback to print
    print("Operation completed")
```

---

## Thread Safety

The ErrorEngine is thread-safe for concurrent operations:

```python
# Example: XYMap parallel file loading
def parallel_load_spectra(self):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for fname in self.fnames:
            # Each thread can safely log
            future = executor.submit(self._load_spectrum_worker, fname)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                # Thread-safe exception handling
                error_engine.handle_exception(
                    e,
                    context="Parallel spectrum loading",
                    show_user_message=False
                )
```

---

## Backward Compatibility

### Existing Code Remains Functional
- All existing try/except blocks continue to work
- Print statements are still output to console
- Flag-based error checking (e.g., `dataokay`) still works
- No breaking changes to existing APIs

### Gradual Migration Path
1. **Phase 1**: Add ErrorEngine logging to existing try/except blocks
2. **Phase 2**: Replace simple try/except with context managers
3. **Phase 3**: Add decorators to high-level functions
4. **Phase 4**: Remove redundant print statements

---

## Troubleshooting

### ErrorEngine Not Initialized
**Error:** `RuntimeError: ErrorEngine not initialized`

**Solution:**
```python
# Initialize at application startup
logger = ee.setup_logger("SpecMap", "logs")
error_engine = ee.initialize_error_engine(logger)
```

### Log Files Not Created
**Check:**
1. `logs/` directory permissions
2. Disk space
3. ErrorEngine initialization in main9.py

### Messageboxes Not Appearing
**Possible causes:**
1. `show_messagebox=False` in initialization
2. `show_user_message=False` in handle_exception call
3. Tkinter not initialized yet

---

## Extending ErrorEngine

### Adding Custom Context Information

```python
class CustomErrorEngine(ee.ErrorEngine):
    def handle_exception(self, exception, context="", **kwargs):
        # Add application-specific context
        kwargs.setdefault('additional_info', {})
        kwargs['additional_info']['app_version'] = "1.0"
        kwargs['additional_info']['active_tab'] = self.get_active_tab()
        
        super().handle_exception(exception, context, **kwargs)
```

### Custom Error Messages

```python
def _create_user_message(self, error_type, error_msg, context):
    # Add custom error message formatting
    if "network" in error_msg.lower():
        return "Network error occurred. Check your connection."
    
    return super()._create_user_message(error_type, error_msg, context)
```

---

## Performance Considerations

- **Minimal Overhead**: ErrorEngine adds negligible overhead (<1ms per log entry)
- **Async Logging**: File writes are buffered by Python's logging module
- **Rotation Efficiency**: Log rotation only occurs when file size exceeds 5MB
- **Thread Locks**: Only used when necessary for thread-local storage

---

## Testing Error Handling

### Manual Testing
```python
# Test file not found error
try:
    with open("/nonexistent/file.txt") as f:
        data = f.read()
except Exception as e:
    error_engine.handle_exception(e, context="Testing error handling")

# Test pickle error
try:
    with open("/tmp/bad.pkl", 'wb') as f:
        pickle.dump(lambda x: x, f)  # Will fail
except Exception as e:
    error_engine.handle_exception(e, context="Testing pickle error")
```

### Verify Logging
1. Check `logs/specmap.log` exists
2. Verify log format is correct
3. Confirm context information is captured
4. Check log rotation (create >5MB of logs)

---

## Additional Resources

- **Module Source**: `error_engine.py`
- **Integration Examples**: `main9.py`, `lib9.py`
- **Python Logging Docs**: https://docs.python.org/3/library/logging.html

---

**Version:** 1.0  
**Last Updated:** January 12, 2026  
**Maintainer:** PyProgMo
