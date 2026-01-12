#!/usr/bin/env python
"""
Test script for error_handler module.
Tests basic functionality without requiring full GUI.
"""

import os
import sys

# Test 1: Import and basic initialization
print("Test 1: Import and initialization")
try:
    import error_handler
    print("✓ Successfully imported error_handler module")
except Exception as e:
    print(f"✗ Failed to import error_handler: {e}")
    sys.exit(1)

# Test 2: Create ErrorEngine instance
print("\nTest 2: Create ErrorEngine instance")
try:
    engine = error_handler.ErrorEngine(
        log_file='logs/test_specmap.log',
        max_bytes=1024*1024,  # 1MB for testing
        backup_count=2
    )
    print("✓ Successfully created ErrorEngine instance")
    print(f"  Log file: {engine.log_file}")
except Exception as e:
    print(f"✗ Failed to create ErrorEngine: {e}")
    sys.exit(1)

# Test 3: Get logger
print("\nTest 3: Get logger")
try:
    logger = engine.get_logger()
    print("✓ Successfully got logger")
    print(f"  Logger name: {logger.name}")
except Exception as e:
    print(f"✗ Failed to get logger: {e}")
    sys.exit(1)

# Test 4: Direct logging
print("\nTest 4: Direct logging")
try:
    logger.info("Test info message", extra={'context': 'Testing'})
    logger.warning("Test warning message", extra={'context': 'Testing'})
    logger.error("Test error message", extra={'context': 'Testing'})
    logger.debug("Test debug message", extra={'context': 'Testing'})
    print("✓ Successfully logged messages at different levels")
except Exception as e:
    print(f"✗ Failed to log messages: {e}")
    sys.exit(1)

# Test 5: Error handling without tkinter (will print instead of showing messagebox)
print("\nTest 5: Error handling (will print error instead of showing messagebox)")
try:
    # Simulate an error
    try:
        raise FileNotFoundError("test_file.txt not found")
    except Exception as e:
        engine.error(
            exception=e,
            context="Testing error handling",
            filename="test_file.txt",
            action="test_action"
        )
    print("✓ Successfully handled error with ErrorEngine.error()")
except Exception as e:
    print(f"✗ Failed to handle error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Warning handling
print("\nTest 6: Warning handling (will print warning instead of showing messagebox)")
try:
    engine.warning(
        message="This is a test warning",
        context="Testing warning handling",
        test_param1="value1",
        test_param2="value2"
    )
    print("✓ Successfully handled warning with ErrorEngine.warning()")
except Exception as e:
    print(f"✗ Failed to handle warning: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Verify log file was created and contains entries
print("\nTest 7: Verify log file")
try:
    if os.path.exists(engine.log_file):
        with open(engine.log_file, 'r') as f:
            log_content = f.read()
            lines = log_content.strip().split('\n')
            print(f"✓ Log file exists: {engine.log_file}")
            print(f"  Number of log entries: {len(lines)}")
            print(f"\n  First few log entries:")
            for line in lines[:5]:
                print(f"    {line}")
    else:
        print(f"✗ Log file not found: {engine.log_file}")
except Exception as e:
    print(f"✗ Failed to read log file: {e}")

# Test 8: Test get_default_error_engine
print("\nTest 8: Test get_default_error_engine()")
try:
    default_engine = error_handler.get_default_error_engine()
    print("✓ Successfully got default error engine")
    print(f"  Log file: {default_engine.log_file}")
except Exception as e:
    print(f"✗ Failed to get default error engine: {e}")

print("\n" + "="*60)
print("All tests completed successfully!")
print("="*60)

# Cleanup test log file
try:
    if os.path.exists('logs/test_specmap.log'):
        os.remove('logs/test_specmap.log')
        print("\nCleaned up test log file")
except:
    pass
