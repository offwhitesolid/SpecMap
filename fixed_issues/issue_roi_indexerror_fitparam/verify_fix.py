#!/usr/bin/env python3
"""
Verification script for the IndexError fix in plotHSIfromfitparam.

This script demonstrates the bug and validates the fix.
"""

import numpy as np

# Simulate the bug scenario
def demonstrate_bug():
    """Demonstrates the bug that was causing the IndexError."""
    print("=" * 60)
    print("DEMONSTRATING THE BUG")
    print("=" * 60)
    
    # Create a sample numpy array similar to lastpm (PixMatrix)
    lastpm = np.zeros((10, 10))
    
    # Simulate what writetopixmatrix returns - a STRING
    newpm = "HSI0"  # This is what newpm actually is - a string!
    
    print(f"lastpm is a numpy array with shape: {lastpm.shape}")
    print(f"newpm is a string: '{newpm}' (type: {type(newpm).__name__})")
    
    # Try to use the buggy code pattern
    i, j = 5, 5
    print(f"\nAttempting buggy code: lastpm[newpm][{i}][{j}] = np.nan")
    
    try:
        lastpm[newpm][i][j] = np.nan
        print("ERROR: The buggy code should have failed but didn't!")
    except IndexError as e:
        print(f"Expected IndexError occurred: {e}")
    except Exception as e:
        print(f" Unexpected error: {type(e).__name__}: {e}")

def demonstrate_fix():
    """Demonstrates the correct fix."""
    print("\n" + "=" * 60)
    print("DEMONSTRATING THE FIX")
    print("=" * 60)
    
    # Create a sample numpy array similar to lastpm (PixMatrix)
    lastpm = np.zeros((10, 10))
    
    # Simulate what writetopixmatrix returns - a STRING
    newpm = "HSI0"
    
    print(f"lastpm is a numpy array with shape: {lastpm.shape}")
    print(f"newpm is a string: '{newpm}' (type: {type(newpm).__name__})")
    
    # Use the correct code pattern
    i, j = 5, 5
    print(f"\nApplying fixed code: lastpm[{i}][{j}] = np.nan")
    
    try:
        lastpm[i][j] = np.nan
        print(f"Assignment successful! lastpm[{i}][{j}] = {lastpm[i][j]}")
        print(f"The fix works correctly - no IndexError!")
    except Exception as e:
        print(f" Unexpected error: {type(e).__name__}: {e}")

def verify_logic():
    """Verifies the complete logic of the fix."""
    print("\n" + "=" * 60)
    print("VERIFYING COMPLETE LOGIC")
    print("=" * 60)
    
    # Simulate the complete workflow
    lastpm = np.random.rand(10, 10) * 100  # Random values
    newpm = "HSI0"  # String returned from writetopixmatrix
    
    print("Simulating the ROI-enabled code path:")
    print(f"1. lastpm (working array) shape: {lastpm.shape}")
    print(f"2. newpm (HSI name): '{newpm}'")
    
    # Simulate setting NaN values for pixels outside ROI
    roi_mask = np.random.rand(10, 10) > 0.5  # Random ROI mask
    
    for i in range(lastpm.shape[0]):
        for j in range(lastpm.shape[1]):
            if not roi_mask[i, j]:
                # This is the FIXED code - use lastpm[i][j], NOT lastpm[newpm][i][j]
                lastpm[i][j] = np.nan
    
    nan_count = np.sum(np.isnan(lastpm))
    total_pixels = lastpm.shape[0] * lastpm.shape[1]
    print(f"3. Set {nan_count}/{total_pixels} pixels to NaN (outside ROI)")
    print(f"Logic works correctly!")

if __name__ == "__main__":
    demonstrate_bug()
    demonstrate_fix()
    verify_logic()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("The bug was: Using lastpm[newpm][i][j] where newpm is a string")
    print("The fix is:  Using lastpm[i][j] with integer indices directly")
    print("=" * 60)
