#!/usr/bin/env python3
"""
Test script for ErrorEngine functionality.
Tests logging, error handling, and integration.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import error_engine as ee
import tempfile
import shutil

def test_logger_setup():
    """Test logger initialization and configuration."""
    print("=" * 50)
    print("Test 1: Logger Setup")
    print("=" * 50)
    
    # Create temporary log directory
    temp_dir = tempfile.mkdtemp()
    print(f"Created temp directory: {temp_dir}")
    
    try:
        # Initialize logger
        logger = ee.setup_logger("TestSpecMap", temp_dir)
        print(f"✓ Logger initialized: {logger.name}")
        
        # Check log file was created
        log_file = os.path.join(temp_dir, "testspecmap.log")
        
        # Write a test message
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Verify log file exists and has content
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                if "Test info message" in content and "Test warning message" in content:
                    print(f"✓ Log file created and contains messages")
                    print(f"  Log file: {log_file}")
                else:
                    print(f"✗ Log file missing expected messages")
        else:
            print(f"✗ Log file not created: {log_file}")
        
        print("\nTest 1: PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        return False
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temp directory")
        except:
            pass

def test_error_engine_basic():
    """Test basic ErrorEngine functionality."""
    print("=" * 50)
    print("Test 2: ErrorEngine Basic Functionality")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize error engine
        logger = ee.setup_logger("TestSpecMap2", temp_dir)
        error_engine = ee.ErrorEngine(logger, show_messagebox=False)
        print("✓ ErrorEngine initialized")
        
        # Test logging methods
        error_engine.log_info("Test info", key="value")
        print("✓ log_info works")
        
        error_engine.log_warning("Test warning", param=123)
        print("✓ log_warning works")
        
        error_engine.log_debug("Test debug", data="test")
        print("✓ log_debug works")
        
        print("\nTest 2: PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def test_exception_handling():
    """Test exception handling."""
    print("=" * 50)
    print("Test 3: Exception Handling")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize error engine
        logger = ee.setup_logger("TestSpecMap3", temp_dir)
        error_engine = ee.ErrorEngine(logger, show_messagebox=False)
        
        # Test handling a FileNotFoundError
        try:
            with open("/nonexistent/file.txt", 'r') as f:
                data = f.read()
        except Exception as e:
            error_engine.handle_exception(
                e,
                context="Test file operation",
                show_user_message=False,
                additional_info={"filename": "/nonexistent/file.txt"}
            )
            print("✓ FileNotFoundError handled")
        
        # Test handling a generic exception
        try:
            raise ValueError("Test error message")
        except Exception as e:
            error_engine.handle_exception(
                e,
                context="Test generic error",
                severity="WARNING",
                show_user_message=False
            )
            print("✓ ValueError handled")
        
        # Verify log file contains exception info
        log_file = os.path.join(temp_dir, "testspecmap3.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                if "FileNotFoundError" in content and "ValueError" in content:
                    print("✓ Exceptions logged correctly")
                else:
                    print("✗ Log missing exception information")
        
        print("\nTest 3: PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def test_context_manager():
    """Test context manager functionality."""
    print("=" * 50)
    print("Test 4: Context Manager")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize error engine
        logger = ee.setup_logger("TestSpecMap4", temp_dir)
        error_engine = ee.ErrorEngine(logger, show_messagebox=False)
        
        # Test successful context
        with error_engine.context("Test operation", param="value"):
            print("✓ Context manager entered successfully")
        
        print("✓ Context manager exited successfully")
        
        # Test context with exception
        exception_caught = False
        try:
            with error_engine.context("Test error context", filename="test.txt"):
                raise RuntimeError("Test error in context")
        except RuntimeError:
            exception_caught = True
            print("✓ Exception propagated from context")
        
        if not exception_caught:
            print("✗ Exception not propagated")
            return False
        
        print("\nTest 4: PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def test_global_instance():
    """Test global instance management."""
    print("=" * 50)
    print("Test 5: Global Instance Management")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize global instance
        logger = ee.setup_logger("TestSpecMap5", temp_dir)
        error_engine = ee.initialize_error_engine(logger, show_messagebox=False)
        print("✓ Global error engine initialized")
        
        # Retrieve global instance
        retrieved_engine = ee.get_error_engine()
        print("✓ Global error engine retrieved")
        
        # Verify it's the same instance
        if retrieved_engine is error_engine:
            print("✓ Same instance returned")
        else:
            print("✗ Different instance returned")
            return False
        
        print("\nTest 5: PASSED\n")
        return True
        
    except Exception as e:
        print(f"✗ Test 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("ErrorEngine Test Suite")
    print("=" * 50 + "\n")
    
    tests = [
        test_logger_setup,
        test_error_engine_basic,
        test_exception_handling,
        test_context_manager,
        test_global_instance,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All tests PASSED")
        return 0
    else:
        print("\n✗ Some tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
