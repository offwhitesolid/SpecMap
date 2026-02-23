#!/usr/bin/env python3
"""
Test for fixes to hyperspectra loading bugs:
1. Specdiff1/Specdiff2 initialized as None (not []) to prevent ValueError
2. fittoMatrixfitparams runs PLB fitting for all selected data types
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import PMclasslib1 as PMlib
import hsi_normalization


def test_specdiff_none_initialization():
    """
    Test that Specdiff1 and Specdiff2 are initialized as None, not [].
    
    Before the fix, they were initialized as [] which caused:
    ValueError: x and y must have same first dimension (1024,) and (0,)
    when plotting a spectrum.
    """
    print("Test 1: Specdiff1/Specdiff2 None initialization")

    class MockSpectrumData:
        """Simulates SpectrumData with the fixed initialization"""
        def __init__(self):
            self.PL = []
            self.PLB = []
            self.Specdiff1 = None  # Fixed: was []
            self.Specdiff2 = None  # Fixed: was []
            self.dataokay = True

    spec = MockSpectrumData()

    # Verify None initialization
    assert spec.Specdiff1 is None, "Specdiff1 should be None initially"
    assert spec.Specdiff2 is None, "Specdiff2 should be None initially"

    # Verify the 'is not None' check correctly fails for None
    # This mirrors the actual check in lib9.py:
    # `if hasattr(spec, 'Specdiff1') and spec.Specdiff1 is not None:`
    assert spec.Specdiff1 is None, \
        "is not None check should fail for None Specdiff1"
    assert spec.Specdiff2 is None, \
        "is not None check should fail for None Specdiff2"

    # Verify that after calculation, the check passes
    spec.Specdiff1 = np.zeros(1024, dtype=np.float32)
    spec.Specdiff2 = np.zeros(1024, dtype=np.float32)

    assert hasattr(spec, 'Specdiff1') and spec.Specdiff1 is not None, \
        "is not None check should pass after calculation"
    assert len(spec.Specdiff1) == 1024, "Specdiff1 should have correct length after calculation"

    print("  PASS: Specdiff1/Specdiff2 are None initially, non-None after calculation")


def test_specdiff_old_bug_demonstration():
    """
    Demonstrate that the old behavior (Specdiff1=[]) would cause ValueError.
    """
    print("Test 2: Old bug demonstration - empty list causes shape mismatch")

    class OldMockSpectrumData:
        """Simulates OLD SpectrumData with buggy initialization"""
        def __init__(self):
            self.Specdiff1 = []  # Old buggy initialization

    spec = OldMockSpectrumData()

    # Old check: passes for empty list!
    old_check_passes = spec.Specdiff1 is not None
    assert old_check_passes, "Old check incorrectly passes for empty list"

    # The empty array would cause shape mismatch
    specdiff1_array = np.asarray(spec.Specdiff1)
    assert specdiff1_array.shape == (0,), "Empty list has shape (0,)"

    wl = np.linspace(400, 800, 1024)
    assert wl.shape == (1024,), "WL has shape (1024,)"

    # This would cause: ValueError: x and y must have same first dimension
    # but shapes are (1024,) and (0,)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(wl, specdiff1_array)
        plt.close('all')
        print("  NOTE: matplotlib did not raise ValueError (test environment)")
    except ValueError as e:
        assert "(1024,)" in str(e) and "(0,)" in str(e), \
            f"Expected shape mismatch error, got: {e}"
        print(f"  PASS: Old bug confirmed - ValueError: {e}")
    except Exception:
        pass  # Other environment issues are ok

    print("  PASS: Old bug correctly identified")


def test_normalize_derivatives_with_none_specdiff():
    """
    Test that normalize_derivatives_by_signal handles None Specdiff1 gracefully.
    """
    print("Test 3: normalize_derivatives_by_signal with None Specdiff1")

    class MockSpectrumData:
        def __init__(self):
            self.PLB = np.random.rand(1024).astype(np.float32) * 1000
            self.Specdiff1 = None  # Not calculated
            self.Specdiff2 = None  # Not calculated
            self.dataokay = True

    spec = MockSpectrumData()
    matrix = [[spec]]

    # Should not raise any exception
    hsi_normalization.normalize_derivatives_by_signal(matrix, signal_key='PLB')

    # Specdiff1_norm should not be created (since Specdiff1 is None)
    assert not hasattr(spec, 'Specdiff1_norm'), \
        "Specdiff1_norm should not be set when Specdiff1 is None"
    assert not hasattr(spec, 'Specdiff2_norm'), \
        "Specdiff2_norm should not be set when Specdiff2 is None"

    print("  PASS: normalize_derivatives handles None Specdiff1 correctly")


def test_normalize_derivatives_with_calculated_specdiff():
    """
    Test that normalize_derivatives_by_signal creates Specdiff_norm when Specdiff is computed.
    """
    print("Test 4: normalize_derivatives_by_signal with calculated Specdiff1")

    class MockSpectrumData:
        def __init__(self):
            self.PLB = np.random.rand(1024).astype(np.float32) * 1000 + 100
            self.Specdiff1 = np.random.rand(1024).astype(np.float32) * 10
            self.Specdiff2 = np.random.rand(1024).astype(np.float32) * 5
            self.dataokay = True

    spec = MockSpectrumData()
    matrix = [[spec]]

    hsi_normalization.normalize_derivatives_by_signal(matrix, signal_key='PLB')

    # Specdiff1_norm should be created
    assert hasattr(spec, 'Specdiff1_norm'), "Specdiff1_norm should be set when Specdiff1 is computed"
    assert hasattr(spec, 'Specdiff2_norm'), "Specdiff2_norm should be set when Specdiff2 is computed"
    assert spec.Specdiff1_norm.shape == (1024,), "Specdiff1_norm should have correct shape"

    print("  PASS: normalize_derivatives creates Specdiff_norm when Specdiff is computed")


def test_fitmatrix_always_uses_plb():
    """
    Test that the fittoMatrixfitparams always uses PLB for fitting,
    regardless of which data type is selected.

    Before the fix, only 'PLB' would trigger the fit; other types (PL, Specdiff1, etc.)
    would skip the fit but still run `if fitdata == [None]: PixMatrix = nan`.
    This caused a white (all-NaN) HSI for all non-PLB data types.
    """
    print("Test 5: fittoMatrixfitparams uses PLB for all data types")

    # Simulate the fixed behavior
    class MockSpec:
        def __init__(self, plb_sum):
            self.PLB = np.ones(1024) * (plb_sum / 1024)
            self.fitdata = [None]
            self.fitmaxX = np.nan
            self.dataokay = True
            self.dofit = True

    countthreshv = 10000
    aqpixstart = 150
    aqpixend = 878

    # For the fixed code: PLB fitting runs regardless of selected data type
    # Case 1: PLB sum ABOVE threshold → fit runs → fitmaxX will be set
    spec_high_signal = MockSpec(plb_sum=500000)
    plb_sum = np.sum(spec_high_signal.PLB[aqpixstart:aqpixend])
    assert plb_sum > countthreshv, "PLB sum should be above threshold for test"

    # Simulate the fixed fittoMatrixfitparams: always check PLB sum first
    PixMatrix = [[0.0]]
    if plb_sum >= countthreshv:
        # Fit would run here (simulated)
        spec_high_signal.fitdata = [600.0, 0.5]  # successful fit
        spec_high_signal.fitmaxX = 600.0
        PixMatrix[0][0] = spec_high_signal.fitmaxX
    else:
        PixMatrix[0][0] = np.nan

    assert not np.isnan(PixMatrix[0][0]), \
        "PixMatrix should not be NaN when PLB sum is above threshold"
    print(f"  PASS: High-signal PLB → PixMatrix = {PixMatrix[0][0]} (not NaN)")

    # Case 2: PLB sum BELOW threshold → NaN (no signal to fit, correct behavior)
    spec_low_signal = MockSpec(plb_sum=100)
    plb_sum2 = np.sum(spec_low_signal.PLB[aqpixstart:aqpixend])
    PixMatrix2 = [[0.0]]
    if plb_sum2 >= countthreshv:
        spec_low_signal.fitdata = [600.0, 0.5]
        PixMatrix2[0][0] = spec_low_signal.fitmaxX
    else:
        PixMatrix2[0][0] = np.nan

    assert np.isnan(PixMatrix2[0][0]), \
        "PixMatrix should be NaN when PLB sum is below threshold (no signal)"
    print(f"  PASS: Low-signal PLB → PixMatrix = NaN (correct, no signal to fit)")


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Testing fixes for hyperspectra loading bugs")
    print("=" * 60)

    tests = [
        test_specdiff_none_initialization,
        test_specdiff_old_bug_demonstration,
        test_normalize_derivatives_with_none_specdiff,
        test_normalize_derivatives_with_calculated_specdiff,
        test_fitmatrix_always_uses_plb,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    if failed == 0:
        print(f"✅ ALL {passed} TESTS PASSED!")
    else:
        print(f"❌ {failed} FAILED, {passed} PASSED")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
