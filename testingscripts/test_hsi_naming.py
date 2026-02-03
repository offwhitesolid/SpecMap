#!/usr/bin/env python3
"""
Test script to verify HSI naming uniqueness with counter.
Tests that HSI names never duplicate even after deletion and loading.
"""

import numpy as np
import sys
import os
import tempfile
import pickle

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lib9
import PMclasslib1 as PMlib
import tkinter as tk

def create_test_xymap():
    """Create a minimal XYMap instance for testing."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create frames
    cmapframe = tk.Frame(root)
    specframe = tk.Frame(root)
    
    # Create XYMap with empty files list
    xymap = lib9.XYMap([], cmapframe, specframe, skip_gui_build=True)
    
    # Initialize required attributes for testing
    xymap.PixAxX = np.array([0, 1, 2])
    xymap.PixAxY = np.array([0, 1, 2])
    xymap.PMmetadata = {}
    xymap.wlstart = 500
    xymap.wlend = 600
    xymap.countthreshv = 0
    xymap.aqpixstart = 0
    xymap.aqpixend = 100
    
    return xymap, root

def test_counter_initialization():
    """Test that counter is initialized to 0."""
    print("Test 1: Counter initialization")
    xymap, root = create_test_xymap()
    
    assert hasattr(xymap, '_hsi_counter'), "HSI counter not initialized"
    assert xymap._hsi_counter == 0, f"Counter should be 0, got {xymap._hsi_counter}"
    
    print("✅ Counter initialized correctly\n")
    root.destroy()
    return True

def test_writetopixmatrix_increments():
    """Test that writetopixmatrix increments the counter."""
    print("Test 2: writetopixmatrix increments counter")
    xymap, root = create_test_xymap()
    
    # Create test matrices
    matrix1 = np.array([[1, 2], [3, 4]])
    matrix2 = np.array([[5, 6], [7, 8]])
    matrix3 = np.array([[9, 10], [11, 12]])
    
    # Add HSIs
    name1 = xymap.writetopixmatrix(matrix1)
    assert name1 == 'HSI0', f"First HSI should be HSI0, got {name1}"
    assert xymap._hsi_counter == 1, f"Counter should be 1, got {xymap._hsi_counter}"
    
    name2 = xymap.writetopixmatrix(matrix2)
    assert name2 == 'HSI1', f"Second HSI should be HSI1, got {name2}"
    assert xymap._hsi_counter == 2, f"Counter should be 2, got {xymap._hsi_counter}"
    
    name3 = xymap.writetopixmatrix(matrix3)
    assert name3 == 'HSI2', f"Third HSI should be HSI2, got {name3}"
    assert xymap._hsi_counter == 3, f"Counter should be 3, got {xymap._hsi_counter}"
    
    print(f"  Created HSIs: {name1}, {name2}, {name3}")
    print(f"  Counter value: {xymap._hsi_counter}")
    print("✅ Counter increments correctly\n")
    root.destroy()
    return True

def test_deletion_doesnt_reuse_names():
    """Test that deleting an HSI doesn't cause name reuse."""
    print("Test 3: Deletion doesn't reuse names")
    xymap, root = create_test_xymap()
    
    # Add HSIs
    matrix = np.array([[1, 2], [3, 4]])
    name1 = xymap.writetopixmatrix(matrix)
    name2 = xymap.writetopixmatrix(matrix)
    name3 = xymap.writetopixmatrix(matrix)
    
    print(f"  Created: {name1}, {name2}, {name3}")
    assert name1 == 'HSI0'
    assert name2 == 'HSI1'
    assert name3 == 'HSI2'
    
    # Delete HSI1
    del xymap.PMdict[name2]
    print(f"  Deleted: {name2}")
    print(f"  Remaining HSIs: {list(xymap.PMdict.keys())}")
    
    # Create new HSI - should be HSI3, not HSI1
    name4 = xymap.writetopixmatrix(matrix)
    print(f"  New HSI after deletion: {name4}")
    assert name4 == 'HSI3', f"New HSI should be HSI3, got {name4}"
    assert 'HSI1' not in xymap.PMdict or name4 != 'HSI1', "Name HSI1 should not be reused"
    
    print("✅ Names not reused after deletion\n")
    root.destroy()
    return True

def test_save_load_preserves_counter():
    """Test that save/load preserves the counter."""
    print("Test 4: Save/load preserves counter")
    xymap, root = create_test_xymap()
    
    # Add some HSIs
    matrix = np.array([[1, 2], [3, 4]])
    name1 = xymap.writetopixmatrix(matrix)
    name2 = xymap.writetopixmatrix(matrix)
    
    print(f"  Created HSIs before save: {name1}, {name2}")
    print(f"  Counter before save: {xymap._hsi_counter}")
    
    # Save state
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        temp_file = f.name
    
    try:
        xymap.save_state(temp_file)
        print(f"  State saved to {temp_file}")
        
        # Create new XYMap and load
        xymap2, root2 = create_test_xymap()
        xymap2.load_state(temp_file)
        
        print(f"  Counter after load: {xymap2._hsi_counter}")
        print(f"  Loaded HSIs: {list(xymap2.PMdict.keys())}")
        
        # Counter should be at least 2 (since we created HSI0 and HSI1)
        assert xymap2._hsi_counter >= 2, f"Counter should be >= 2, got {xymap2._hsi_counter}"
        
        # Create new HSI - should be HSI2 or higher
        name3 = xymap2.writetopixmatrix(matrix)
        print(f"  New HSI after load: {name3}")
        
        # Verify no duplicates
        assert name3 not in [name1, name2], f"New HSI {name3} duplicates existing names"
        
        print("✅ Counter preserved across save/load\n")
        root2.destroy()
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    root.destroy()
    return True

def test_load_with_high_numbered_hsis():
    """Test that loading a state with high-numbered HSIs updates counter correctly."""
    print("Test 5: Load state with high-numbered HSIs")
    xymap, root = create_test_xymap()
    
    # Manually create HSIs with high numbers to simulate loaded state
    matrix = np.array([[1, 2], [3, 4]])
    xymap.PMdict['HSI10'] = PMlib.PMclass(matrix, xymap.PixAxX, xymap.PixAxY, xymap.PMmetadata)
    xymap.PMdict['HSI20'] = PMlib.PMclass(matrix, xymap.PixAxX, xymap.PixAxY, xymap.PMmetadata)
    
    # Save and reload to trigger counter update logic
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        temp_file = f.name
    
    try:
        xymap.save_state(temp_file)
        
        # Create new XYMap and load
        xymap2, root2 = create_test_xymap()
        xymap2.load_state(temp_file)
        
        print(f"  Loaded HSIs: {list(xymap2.PMdict.keys())}")
        print(f"  Counter after load: {xymap2._hsi_counter}")
        
        # Counter should be > 20 to avoid conflicts
        assert xymap2._hsi_counter > 20, f"Counter should be > 20, got {xymap2._hsi_counter}"
        
        # Create new HSI
        name_new = xymap2.writetopixmatrix(matrix)
        print(f"  New HSI: {name_new}")
        
        # Verify it doesn't conflict
        assert name_new not in ['HSI10', 'HSI20'], f"New HSI {name_new} conflicts with existing"
        
        print("✅ Counter correctly updated for high-numbered HSIs\n")
        root2.destroy()
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    root.destroy()
    return True

def test_all_hsi_names_unique():
    """Test that all HSI names remain unique through complex operations."""
    print("Test 6: Complex scenario - all names unique")
    xymap, root = create_test_xymap()
    
    matrix = np.array([[1, 2], [3, 4]])
    all_names = []
    
    # Create several HSIs
    for i in range(5):
        name = xymap.writetopixmatrix(matrix)
        all_names.append(name)
    
    print(f"  Created 5 HSIs: {all_names}")
    
    # Delete some
    del xymap.PMdict[all_names[1]]
    del xymap.PMdict[all_names[3]]
    print(f"  Deleted: {all_names[1]}, {all_names[3]}")
    
    # Create more
    for i in range(3):
        name = xymap.writetopixmatrix(matrix)
        all_names.append(name)
    
    print(f"  Created 3 more HSIs: {all_names[5:]}")
    
    # Check uniqueness
    unique_names = set(all_names)
    assert len(unique_names) == len(all_names), f"Duplicate names found! {len(all_names)} total, {len(unique_names)} unique"
    
    print(f"  All {len(all_names)} names are unique")
    print("✅ Complex scenario passed\n")
    root.destroy()
    return True

def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("HSI Naming Uniqueness Tests")
    print("="*60)
    print()
    
    tests = [
        test_counter_initialization,
        test_writetopixmatrix_increments,
        test_deletion_doesnt_reuse_names,
        test_save_load_preserves_counter,
        test_load_with_high_numbered_hsis,
        test_all_hsi_names_unique,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} raised exception: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
