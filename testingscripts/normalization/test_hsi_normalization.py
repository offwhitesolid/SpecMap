"""
Simple test script for HSI normalization module
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

import hsi_normalization

# Mock SpectrumData class for testing
class MockSpectrumData:
    def __init__(self, plb_data, specdiff1_data=None, specdiff2_data=None):
        self.PLB = plb_data
        self.PL = plb_data
        self.BG = np.zeros_like(plb_data)
        self.Specdiff1 = specdiff1_data if specdiff1_data is not None else np.zeros_like(plb_data)
        self.Specdiff2 = specdiff2_data if specdiff2_data is not None else np.zeros_like(plb_data)
        self.dataokay = True

def test_normalize_none():
    """Test no normalization - should return matrix of 1s"""
    print("Testing normalize_none...")
    
    # Create mock data
    wl = np.linspace(500, 700, 100)
    spec_matrix = [[MockSpectrumData(np.random.rand(100) * 1000) for _ in range(3)] for _ in range(3)]
    
    # Create normalizer
    normalizer = hsi_normalization.HSINormalization(spec_matrix, wl)
    
    # Generate normalization matrix
    norm_matrix = normalizer.generate_normalization_matrix('none')
    
    # Check that all values are 1
    assert np.all(norm_matrix == 1.0), "normalize_none should return all 1s"
    print("✓ normalize_none passed")

def test_normalize_integrated_counts():
    """Test normalization by integrated counts"""
    print("Testing normalize_integrated_counts...")
    
    # Create mock data with known values
    wl = np.linspace(500, 700, 100)
    
    # Create spectrum with known integrated counts
    spec_data = np.ones(100) * 10  # Each pixel has value 10
    spec_matrix = [[MockSpectrumData(spec_data.copy()) for _ in range(2)] for _ in range(2)]
    
    # Create normalizer
    normalizer = hsi_normalization.HSINormalization(spec_matrix, wl)
    
    # Generate normalization matrix
    params = {'wl_start': 500, 'wl_end': 700, 'data_key': 'PLB'}
    norm_matrix = normalizer.generate_normalization_matrix('integrated_counts', params)
    
    # Integrated counts = 100 pixels * 10 = 1000
    # Normalization value should be 1/1000 = 0.001
    expected_value = 1.0 / 1000.0
    
    assert np.allclose(norm_matrix, expected_value), f"Expected {expected_value}, got {norm_matrix[0][0]}"
    print(f"✓ normalize_integrated_counts passed (norm value: {norm_matrix[0][0]})")

def test_normalize_max_intensity():
    """Test normalization by max intensity"""
    print("Testing normalize_max_intensity...")
    
    # Create mock data with known max value
    wl = np.linspace(500, 700, 100)
    
    # Create spectrum with known max value
    spec_data = np.ones(100) * 10
    spec_data[50] = 100  # Max value is 100
    spec_matrix = [[MockSpectrumData(spec_data.copy()) for _ in range(2)] for _ in range(2)]
    
    # Create normalizer
    normalizer = hsi_normalization.HSINormalization(spec_matrix, wl)
    
    # Generate normalization matrix
    params = {'wl_start': 500, 'wl_end': 700, 'data_key': 'PLB'}
    norm_matrix = normalizer.generate_normalization_matrix('max_intensity', params)
    
    # Max intensity = 100
    # Normalization value should be 1/100 = 0.01
    expected_value = 1.0 / 100.0
    
    assert np.allclose(norm_matrix, expected_value), f"Expected {expected_value}, got {norm_matrix[0][0]}"
    print(f"✓ normalize_max_intensity passed (norm value: {norm_matrix[0][0]})")

def test_normalize_counts_at_wavelength():
    """Test normalization by counts at specific wavelength"""
    print("Testing normalize_counts_at_wavelength...")
    
    # Create mock data
    wl = np.linspace(500, 700, 100)
    
    # Create spectrum with known value at specific wavelength
    spec_data = np.ones(100) * 10
    # At 600nm (index closest to 600), value is 50
    target_idx = np.argmin(np.abs(wl - 600))
    spec_data[target_idx] = 50
    spec_matrix = [[MockSpectrumData(spec_data.copy()) for _ in range(2)] for _ in range(2)]
    
    # Create normalizer
    normalizer = hsi_normalization.HSINormalization(spec_matrix, wl)
    
    # Generate normalization matrix
    params = {'wavelength': 600, 'data_key': 'PLB'}
    norm_matrix = normalizer.generate_normalization_matrix('counts_at_wavelength', params)
    
    # Value at 600nm = 50
    # Normalization value should be 1/50 = 0.02
    expected_value = 1.0 / 50.0
    
    assert np.allclose(norm_matrix, expected_value), f"Expected {expected_value}, got {norm_matrix[0][0]}"
    print(f"✓ normalize_counts_at_wavelength passed (norm value: {norm_matrix[0][0]})")

def test_apply_normalization():
    """Test applying normalization to pixel matrix"""
    print("Testing apply_normalization...")
    
    # Create pixel matrix
    pixel_matrix = np.array([[100, 200], [300, 400]])
    
    # Create normalization matrix
    norm_matrix = np.array([[0.01, 0.01], [0.01, 0.01]])
    
    # Apply normalization
    normalized = hsi_normalization.HSINormalization.apply_normalization(pixel_matrix, norm_matrix)
    
    # Check result
    expected = np.array([[1.0, 2.0], [3.0, 4.0]])
    
    assert np.allclose(normalized, expected), f"Expected {expected}, got {normalized}"
    print("✓ apply_normalization passed")

def test_none_normalization():
    """Test that None normalization matrix returns original data"""
    print("Testing None normalization matrix...")
    
    # Create pixel matrix
    pixel_matrix = np.array([[100, 200], [300, 400]])
    
    # Apply normalization with None
    normalized = hsi_normalization.HSINormalization.apply_normalization(pixel_matrix, None)
    
    # Check that original is returned
    assert np.array_equal(normalized, pixel_matrix), "None normalization should return original"
    print("✓ None normalization passed")

def test_normalize_with_different_dataset():
    """Test normalization using a different dataset than the one being plotted.
    
    This tests the scenario where:
    - User plots derivatives (e.g., Specdiff1)
    - But normalizes by counts from the original PLB signal
    """
    print("Testing normalization with different dataset...")
    
    # Create mock data with different values for PLB and Specdiff1
    wl = np.linspace(500, 700, 100)
    
    # PLB has max value of 100, Specdiff1 has max value of 10
    plb_data = np.ones(100) * 10
    plb_data[50] = 100  # Max value is 100 for PLB
    
    specdiff1_data = np.ones(100) * 1
    specdiff1_data[50] = 10  # Max value is 10 for Specdiff1
    
    spec_matrix = [[MockSpectrumData(plb_data.copy(), specdiff1_data.copy()) for _ in range(2)] for _ in range(2)]
    
    # Create normalizer
    normalizer = hsi_normalization.HSINormalization(spec_matrix, wl)
    
    # Test 1: Normalize using PLB (like normalizing derivatives by original signal)
    params = {'wl_start': 500, 'wl_end': 700, 'data_key': 'PLB'}
    norm_matrix_plb = normalizer.generate_normalization_matrix('max_intensity', params)
    
    # Max intensity of PLB = 100
    # Normalization value should be 1/100 = 0.01
    expected_plb = 1.0 / 100.0
    assert np.allclose(norm_matrix_plb, expected_plb), f"Expected {expected_plb}, got {norm_matrix_plb[0][0]}"
    
    # Test 2: Normalize using Specdiff1 (using derivatives as the normalization source)
    params = {'wl_start': 500, 'wl_end': 700, 'data_key': 'Specdiff1'}
    norm_matrix_diff = normalizer.generate_normalization_matrix('max_intensity', params)
    
    # Max intensity of Specdiff1 = 10
    # Normalization value should be 1/10 = 0.1
    expected_diff = 1.0 / 10.0
    assert np.allclose(norm_matrix_diff, expected_diff), f"Expected {expected_diff}, got {norm_matrix_diff[0][0]}"
    
    print(f"✓ normalization with different dataset passed")
    print(f"  - PLB normalization value: {norm_matrix_plb[0][0]} (expected {expected_plb})")
    print(f"  - Specdiff1 normalization value: {norm_matrix_diff[0][0]} (expected {expected_diff})")

if __name__ == '__main__':
    print("Running HSI Normalization Tests...\n")
    
    try:
        test_normalize_none()
        test_normalize_integrated_counts()
        test_normalize_max_intensity()
        test_normalize_counts_at_wavelength()
        test_apply_normalization()
        test_none_normalization()
        test_normalize_with_different_dataset()
        
        print("\n✓ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
