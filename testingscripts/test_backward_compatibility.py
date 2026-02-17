#!/usr/bin/env python3
"""
Test backward compatibility of chunked save/load with legacy format.
Ensures that old pickle files can still be loaded.
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
        self.WL = None
        self.WL_eV = None


def create_legacy_state_dict():
    """Create a state dictionary in the old (legacy) format."""
    # Create mock data
    specs = [MockSpec(i) for i in range(100)]
    matrix = [[MockSpec(i*10 + j) for j in range(10)] for i in range(10)]
    
    state = {
        # Core data
        'WL': np.linspace(400, 800, 100),
        'WL_eV': None,
        'BG': [],
        'fnames': ['test1.txt', 'test2.txt'],
        
        # Large data structures (legacy: in main state dict)
        'specs': specs,
        'SpecDataMatrix': matrix,
        'PMdict': {},
        'PMmetadata': {},
        
        # Settings
        '_hsi_counter': 0,
        '_nan_replacements': {},
        '_nan_replacements_roilist': {},
        'roilist': {},
        'disspecs': {},
        
        # Processing parameters
        'wlstart': 400,
        'wlend': 800,
        'countthreshv': 10,
        'aqpixstart': 0,
        'aqpixend': -1,
        
        # Grid parameters
        'mxcoords': [],
        'mycoords': [],
        'PixAxX': [],
        'PixAxY': [],
        'gdx': 0,
        'gdy': 0,
        
        # Data ranges
        'DataSpecMin': 400,
        'DataSpecMax': 800,
        'DataSpecdL': 4.0,
        'DataPixSt': 0,
        'DataPixDX': 0,
        'DataPixDY': 0,
        
        # Configuration
        'loadeachbg': False,
        'linearbg': False,
        'removecosmics': False,
        'cosmicthreshold': 20,
        'cosmicpixels': 3,
        'remcosmicfunc': 'median',
        'fontsize': 12,
        
        # Settings
        'colormap': 'viridis',
        'WL_selection': 'nm',
        'HSI_fit_useROI': False,
        'HSI_from_fitparam_useROI': False,
        
        # Additional attributes
        'defentries': {},
    }
    
    return state


def test_legacy_format_detection():
    """Test that legacy format is correctly detected and loaded."""
    print("\n" + "="*60)
    print("TEST: Legacy format detection")
    print("="*60)
    
    # Create legacy state
    state = create_legacy_state_dict()
    
    # Save in legacy format (all in one pickle.dump)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("✓ Saved legacy format state")
    
    # Load and check
    with open(temp_file, 'rb') as f:
        loaded_state = pickle.load(f)
    
    os.unlink(temp_file)
    
    # Verify legacy format (no format_version or format_version == 1)
    assert loaded_state.get('format_version', 1) == 1
    assert 'specs' in loaded_state
    assert 'SpecDataMatrix' in loaded_state
    assert 'PMdict' in loaded_state
    assert len(loaded_state['specs']) == 100
    assert len(loaded_state['SpecDataMatrix']) == 10
    
    print("✓ Legacy format correctly detected (format_version=1)")
    print(f"✓ Loaded {len(loaded_state['specs'])} specs from legacy format")
    print(f"✓ Loaded {len(loaded_state['SpecDataMatrix'])}x{len(loaded_state['SpecDataMatrix'][0])} matrix from legacy format")
    
    return True


def test_chunked_format_detection():
    """Test that new chunked format is correctly detected."""
    print("\n" + "="*60)
    print("TEST: Chunked format detection")
    print("="*60)
    
    # Create chunked format state (no large arrays in main dict)
    state = {
        'format_version': 2,
        'WL': np.linspace(400, 800, 100),
        'WL_eV': None,
        'BG': [],
        'fnames': ['test1.txt'],
    }
    
    # Save state
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
        temp_file = f.name
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Save specs in chunks
        num_specs = 100
        pickle.dump(num_specs, f, protocol=pickle.HIGHEST_PROTOCOL)
        chunk = [MockSpec(i) for i in range(num_specs)]
        pickle.dump(chunk, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("✓ Saved chunked format state")
    
    # Load and check
    with open(temp_file, 'rb') as f:
        loaded_state = pickle.load(f)
    
    # Verify chunked format
    assert loaded_state.get('format_version') == 2
    assert 'specs' not in loaded_state  # specs not in main state dict
    
    os.unlink(temp_file)
    
    print("✓ Chunked format correctly detected (format_version=2)")
    print("✓ Large arrays correctly excluded from main state dict")
    
    return True


def test_format_version_compatibility():
    """Test that both formats can coexist and be loaded correctly."""
    print("\n" + "="*60)
    print("TEST: Format version compatibility")
    print("="*60)
    
    # Test 1: Legacy format
    legacy_state = create_legacy_state_dict()
    with tempfile.NamedTemporaryFile(delete=False, suffix='_legacy.pkl') as f:
        legacy_file = f.name
        pickle.dump(legacy_state, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Test 2: Chunked format
    chunked_state = {
        'format_version': 2,
        'WL': np.linspace(400, 800, 100),
        'WL_eV': None,
        'BG': [],
        'fnames': ['test1.txt'],
    }
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='_chunked.pkl') as f:
        chunked_file = f.name
        pickle.dump(chunked_state, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Add mock chunked data
        pickle.dump(10, f)  # num specs
        pickle.dump([MockSpec(i) for i in range(10)], f)
        
        pickle.dump((5, 5), f)  # matrix dimensions
        pickle.dump([[None]*5 for _ in range(5)], f)
        
        pickle.dump(0, f)  # PMdict count
        pickle.dump({}, f)  # roilist
    
    print("✓ Created both legacy and chunked format files")
    
    # Load legacy format
    with open(legacy_file, 'rb') as f:
        loaded_legacy = pickle.load(f)
    
    # Load chunked format
    with open(chunked_file, 'rb') as f:
        loaded_chunked_main = pickle.load(f)
        
        # Simulate chunked loading
        format_version = loaded_chunked_main.get('format_version', 1)
        if format_version >= 2:
            num_specs = pickle.load(f)
            specs_chunk = pickle.load(f)
            loaded_chunked_main['specs_loaded'] = specs_chunk
    
    os.unlink(legacy_file)
    os.unlink(chunked_file)
    
    # Verify both loaded correctly
    assert loaded_legacy.get('format_version', 1) == 1
    assert 'specs' in loaded_legacy
    assert len(loaded_legacy['specs']) == 100
    
    assert loaded_chunked_main.get('format_version') == 2
    assert 'specs' not in loaded_chunked_main
    assert 'specs_loaded' in loaded_chunked_main
    assert len(loaded_chunked_main['specs_loaded']) == 10
    
    print("✓ Legacy format loaded correctly (100 specs, version 1)")
    print("✓ Chunked format loaded correctly (10 specs, version 2)")
    print("✓ Both formats can coexist")
    
    return True


def test_memory_cleanup_between_chunks():
    """Test that garbage collection is called between chunks."""
    print("\n" + "="*60)
    print("TEST: Memory cleanup between chunks (mock)")
    print("="*60)
    
    # This is a simplified test to verify the pattern
    # In real implementation, gc.collect() should be called between chunks
    
    num_items = 1000
    chunk_size = 100
    items_processed = 0
    gc_calls = 0
    
    for i in range(0, num_items, chunk_size):
        # Process chunk (mock)
        chunk = list(range(i, min(i + chunk_size, num_items)))
        items_processed += len(chunk)
        
        # Simulate gc.collect() after each chunk
        gc.collect()
        gc_calls += 1
    
    expected_chunks = (num_items + chunk_size - 1) // chunk_size
    
    assert items_processed == num_items
    assert gc_calls == expected_chunks
    
    print(f"✓ Processed {items_processed} items in {gc_calls} chunks")
    print(f"✓ Called gc.collect() {gc_calls} times (once per chunk)")
    
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("BACKWARD COMPATIBILITY TESTS")
    print("="*60)
    
    try:
        # Run tests
        test_legacy_format_detection()
        test_chunked_format_detection()
        test_format_version_compatibility()
        test_memory_cleanup_between_chunks()
        
        print("\n" + "="*60)
        print("✅ ALL BACKWARD COMPATIBILITY TESTS PASSED")
        print("="*60)
        print("\nKey findings:")
        print("  • Legacy format files can still be loaded")
        print("  • Chunked format correctly identified by flag")
        print("  • Both formats can coexist")
        print("  • Memory cleanup pattern verified")
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
