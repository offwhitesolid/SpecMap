#!/usr/bin/env python3
"""
Demonstration of ErrorEngine functionality.
Shows various usage patterns and error handling scenarios.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import error_engine as ee

def demo_basic_logging():
    """Demonstrate basic logging functionality."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Logging")
    print("="*60)
    
    # Initialize logger
    logger = ee.setup_logger("DemoApp", "logs")
    error_engine = ee.initialize_error_engine(logger, show_messagebox=False)
    
    # Various log levels
    error_engine.log_debug("Application starting", version="1.0")
    error_engine.log_info("Configuration loaded", config_file="config.ini")
    error_engine.log_warning("Using default settings", setting="timeout")
    
    print("✓ Logged messages at DEBUG, INFO, and WARNING levels")
    print("  Check logs/demoapp.log for output")

def demo_exception_handling():
    """Demonstrate exception handling with context."""
    print("\n" + "="*60)
    print("DEMO 2: Exception Handling")
    print("="*60)
    
    error_engine = ee.get_error_engine()
    
    # Simulate file not found error
    try:
        filename = "/tmp/nonexistent_file.txt"
        with open(filename, 'r') as f:
            data = f.read()
    except FileNotFoundError as e:
        error_engine.handle_exception(
            e,
            context="Loading configuration file",
            show_user_message=False,
            additional_info={
                "filename": filename,
                "user_action": "Application startup"
            }
        )
        print("✓ FileNotFoundError caught and logged")
    
    # Simulate processing error
    try:
        data = [1, 2, 3]
        result = data[10]  # Index out of range
    except IndexError as e:
        error_engine.handle_exception(
            e,
            context="Processing data array",
            severity="WARNING",
            show_user_message=False,
            additional_info={
                "array_length": len(data),
                "attempted_index": 10
            }
        )
        print("✓ IndexError caught and logged")

def demo_context_manager():
    """Demonstrate context manager usage."""
    print("\n" + "="*60)
    print("DEMO 3: Context Manager")
    print("="*60)
    
    error_engine = ee.get_error_engine()
    
    # Successful operation with context
    with error_engine.context("Loading user preferences", file="prefs.json"):
        print("  Processing user preferences...")
    print("✓ Context manager logged operation start/end")
    
    # Operation with error
    try:
        with error_engine.context("Parsing configuration", format="JSON"):
            raise ValueError("Invalid JSON format")
    except ValueError:
        print("✓ Exception in context manager logged with full context")

def demo_decorator():
    """Demonstrate decorator usage."""
    print("\n" + "="*60)
    print("DEMO 4: Decorator Pattern")
    print("="*60)
    
    error_engine = ee.get_error_engine()
    
    @error_engine.track_errors(action="Processing data file")
    def process_file(filename):
        """Simulated file processing function."""
        if not filename.endswith('.txt'):
            raise ValueError(f"Expected .txt file, got {filename}")
        print(f"  Processing {filename}...")
        return True
    
    # Call decorated function
    try:
        process_file("data.csv")  # Will raise ValueError
    except ValueError:
        print("✓ Decorator caught and logged exception")

def demo_real_world_scenario():
    """Demonstrate real-world usage scenario."""
    print("\n" + "="*60)
    print("DEMO 5: Real-World Scenario - Data Loading")
    print("="*60)
    
    error_engine = ee.get_error_engine()
    
    # Simulate loading multiple spectrum files
    files = [
        "/tmp/spectrum1.txt",
        "/tmp/spectrum2.txt",
        "/tmp/spectrum3.txt"
    ]
    
    loaded_count = 0
    error_count = 0
    
    for file in files:
        try:
            with error_engine.context("Loading spectrum file", filename=file):
                # Simulate file loading (would normally read file)
                if "spectrum1" in file:
                    print(f"  ✓ Loaded {file}")
                    loaded_count += 1
                else:
                    raise FileNotFoundError(f"File not found: {file}")
        except FileNotFoundError:
            error_count += 1
            print(f"  ✗ Failed to load {file}")
    
    error_engine.log_info(
        "Batch file loading completed",
        loaded=loaded_count,
        errors=error_count,
        total=len(files)
    )
    
    print(f"\n  Summary: Loaded {loaded_count}/{len(files)} files")
    print(f"  All operations logged to logs/demoapp.log")

def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("ErrorEngine Demonstration")
    print("="*70)
    print("\nThis demo shows ErrorEngine handling various error scenarios.")
    print("All operations are logged to: logs/demoapp.log")
    
    try:
        demo_basic_logging()
        demo_exception_handling()
        demo_context_manager()
        demo_decorator()
        demo_real_world_scenario()
        
        print("\n" + "="*70)
        print("Demonstration Complete")
        print("="*70)
        print("\nCheck the log file for detailed output:")
        print("  logs/demoapp.log")
        print("\nLog format:")
        print("  [timestamp] [level] [module:function:line] - message")
        
        # Show last few lines of log
        log_file = "logs/demoapp.log"
        if os.path.exists(log_file):
            print("\nLast 10 entries from log file:")
            print("-" * 70)
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(line.rstrip())
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
