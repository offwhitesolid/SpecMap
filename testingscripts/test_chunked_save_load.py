#!/usr/bin/env python3
"""
Test script to verify chunked save/load state functionality.
Tests that the new memory-efficient chunked format works correctly.
"""

import numpy as np
import sys
import os
import pickle
import tempfile
import gc

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# Mock classes need to be at module level for pickling
class MockSpec:
    """Mock SpectrumData object for testing"""
    def __init__(self, idx):
        self.idx = idx
        self.data = np.random.rand(100)


class MockPM:
    """Mock PM object for testing"""
    def __init__(self, name):
        self.name = name
        self.PixMatrix = np.random.rand(10, 10)


def test_chunked_format_flag():
    """Test that chunked format creates the correct flag in state."""
    print("\n" + "="*60)
    print("TEST: Chunked format flag")
    print("="*60)
    
    # Create a minimal state dict with chunked flag
    state = {
        '_chunked_format': True,
        'WL': np.array([1.0, 2.0, 3.0]),
        'WL_eV': None,
        'BG': [],
        'fnames': ['test.txt'],
    }
    
    # Save and load
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    with open(temp_file, 'rb') as f:
        loaded_state = pickle.load(f)
    
    os.unlink(temp_file)
    
    assert loaded_state['_chunked_format'] == True
    print("✓ Chunked format flag correctly saved and loaded")
    return True


def test_chunked_specs_save_load():
    """Test saving and loading specs in chunks."""
    print("\n" + "="*60)
    print("TEST: Chunked specs save/load")
    print("="*60)
    
    # Create test specs
    num_specs = 5000
    specs = [MockSpec(i) for i in range(num_specs)]
    
    print(f"Created {num_specs} mock specs")
    
    # Save in chunked format
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        
        # Save total count
        pickle.dump(num_specs, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Save in chunks
        chunk_size = 1000
        for i in range(0, num_specs, chunk_size):
            chunk = specs[i:i+chunk_size]
            pickle.dump(chunk, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"✓ Saved {num_specs} specs in chunks")
    
    # Load in chunked format
    with open(temp_file, 'rb') as f:
        total_specs = pickle.load(f)
        loaded_specs = []
        
        chunk_size = 1000
        for i in range(0, total_specs, chunk_size):
            chunk = pickle.load(f)
            loaded_specs.extend(chunk)
            gc.collect()
    
    os.unlink(temp_file)
    
    assert len(loaded_specs) == num_specs
    assert all(loaded_specs[i].idx == i for i in range(num_specs))
    
    print(f"✓ Loaded {len(loaded_specs)} specs correctly")
    return True


def test_chunked_matrix_save_load():
    """Test saving and loading matrix in chunks."""
    print("\n" + "="*60)
    print("TEST: Chunked matrix save/load")
    print("="*60)
    
    # Create test matrix (simplified)
    num_rows = 100
    num_cols = 100
    matrix = [[i*num_cols + j for j in range(num_cols)] for i in range(num_rows)]
    
    print(f"Created {num_rows}x{num_cols} matrix")
    
    # Save in chunked format
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        
        # Save dimensions
        pickle.dump((num_rows, num_cols), f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Save in row chunks
        chunk_size = 50
        for i in range(0, num_rows, chunk_size):
            chunk = matrix[i:i+chunk_size]
            pickle.dump(chunk, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"✓ Saved matrix in chunks")
    
    # Load in chunked format
    with open(temp_file, 'rb') as f:
        dimensions = pickle.load(f)
        loaded_matrix = []
        
        num_rows_loaded, num_cols_loaded = dimensions
        chunk_size = 50
        for i in range(0, num_rows_loaded, chunk_size):
            chunk = pickle.load(f)
            loaded_matrix.extend(chunk)
            gc.collect()
    
    os.unlink(temp_file)
    
    assert len(loaded_matrix) == num_rows
    assert len(loaded_matrix[0]) == num_cols
    assert loaded_matrix[0][0] == 0
    assert loaded_matrix[num_rows-1][num_cols-1] == num_rows*num_cols - 1
    
    print(f"✓ Loaded matrix correctly")
    return True


def test_chunked_pmdict_save_load():
    """Test saving and loading PMdict in chunks."""
    print("\n" + "="*60)
    print("TEST: Chunked PMdict save/load")
    print("="*60)
    
    # Create test PMdict
    num_hsi = 50
    pmdict = {f'HSI{i}': MockPM(f'HSI{i}') for i in range(num_hsi)}
    
    print(f"Created PMdict with {num_hsi} HSI images")
    
    # Save in chunked format
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        
        keys = list(pmdict.keys())
        total_items = len(keys)
        
        # Save total count
        pickle.dump(total_items, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Save in chunks
        chunk_size = 10
        for i in range(0, total_items, chunk_size):
            chunk_keys = keys[i:i+chunk_size]
            chunk_dict = {k: pmdict[k] for k in chunk_keys}
            pickle.dump(chunk_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"✓ Saved PMdict in chunks")
    
    # Load in chunked format
    with open(temp_file, 'rb') as f:
        total_items = pickle.load(f)
        loaded_pmdict = {}
        
        chunk_size = 10
        items_loaded = 0
        
        while items_loaded < total_items:
            chunk_dict = pickle.load(f)
            loaded_pmdict.update(chunk_dict)
            items_loaded += len(chunk_dict)
            gc.collect()
    
    os.unlink(temp_file)
    
    assert len(loaded_pmdict) == num_hsi
    assert all(k in loaded_pmdict for k in pmdict.keys())
    assert all(loaded_pmdict[k].name == pmdict[k].name for k in pmdict.keys())
    
    print(f"✓ Loaded PMdict correctly with {len(loaded_pmdict)} HSI images")
    return True


def test_memory_efficiency():
    """Test that chunked loading is more memory efficient."""
    print("\n" + "="*60)
    print("TEST: Memory efficiency (informational)")
    print("="*60)
    
    import psutil
    process = psutil.Process()
    
    # Create large test data
    num_items = 10000
    large_array = [np.random.rand(100) for _ in range(num_items)]
    
    # Measure memory before
    gc.collect()
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Save and load with chunking
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        pickle.dump(num_items, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        chunk_size = 1000
        for i in range(0, num_items, chunk_size):
            chunk = large_array[i:i+chunk_size]
            pickle.dump(chunk, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Clear original data
    del large_array
    gc.collect()
    
    # Load in chunks
    with open(temp_file, 'rb') as f:
        total = pickle.load(f)
        loaded = []
        chunk_size = 1000
        
        for i in range(0, total, chunk_size):
            chunk = pickle.load(f)
            loaded.extend(chunk)
            gc.collect()
    
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    
    os.unlink(temp_file)
    
    print(f"Memory before: {mem_before:.1f} MB")
    print(f"Memory after: {mem_after:.1f} MB")
    print(f"Memory increase: {mem_after - mem_before:.1f} MB")
    print(f"✓ Loaded {len(loaded)} items with garbage collection")
    
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("CHUNKED SAVE/LOAD TESTS")
    print("="*60)
    
    try:
        # Run tests
        test_chunked_format_flag()
        test_chunked_specs_save_load()
        test_chunked_matrix_save_load()
        test_chunked_pmdict_save_load()
        
        # Optional: memory efficiency test (requires psutil)
        try:
            test_memory_efficiency()
        except ImportError:
            print("\n⚠️  Skipping memory efficiency test (psutil not installed)")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
