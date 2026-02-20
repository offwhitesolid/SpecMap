"""
Test that SpectrumData datasets are stored as float32 numpy arrays.
Validates the RAM optimization described in the issue.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import tempfile

# Check if tkinter is available (required for lib9 import)
try:
    import tkinter as tk
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False


def create_mock_spectrum_file(wl_values, bg_values, pl_values):
    """Create a temporary spectrum file in the expected format."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    tmp.write("Test Spectrum File\n")
    tmp.write("Slit Width (\u00b5m): 100.0\n")
    tmp.write("Central Wavelength (nm): 600.0\n")
    tmp.write("Cooling Temperature (\u00b0C): -69.0\n")
    tmp.write("Exposure Time (s): 1.0\n")
    tmp.write("Delta Wavelength (nm): 0.5\n")
    tmp.write("x-position: 0.0\n")
    tmp.write("y-position: 0.0\n")
    tmp.write("z-position: 0.0\n")
    tmp.write("Short Wavelength (nm): 400.0\n")
    tmp.write("Long Wavelength (nm): 800.0\n")
    tmp.write("magnification: 100.0\n")
    tmp.write("\n")
    # Header line with keys
    tmp.write("WL\tBG\tPL\n")
    for wl, bg, pl in zip(wl_values, bg_values, pl_values):
        tmp.write(f"{wl}\t{bg}\t{pl}\n")
    tmp.close()
    return tmp.name


def test_spectrumdata_float32():
    """Test that SpectrumData stores PL and PLB as float32."""
    if not HAS_TKINTER:
        print("  (skipped: tkinter not available)")
        return

    import lib9 as lib

    n = 50
    wl_vals = np.linspace(450.0, 700.0, n)
    bg_vals = np.full(n, 100)
    pl_vals = np.random.randint(200, 5000, n)

    fname = create_mock_spectrum_file(wl_vals, bg_vals, pl_vals)
    try:
        # Create shared WL and BG as float32 (as loadfiles() would provide)
        shared_wl = np.array(wl_vals, dtype=np.float32)
        shared_bg = np.array(bg_vals, dtype=np.float32)

        spec = lib.SpectrumData(
            filename=fname, WL=shared_wl, BG=shared_bg, loadeachbg=False,
        )

        assert spec.dataokay, "SpectrumData should be OK"
        assert isinstance(spec.PL, np.ndarray), f"PL should be ndarray, got {type(spec.PL)}"
        assert spec.PL.dtype == np.float32, f"PL dtype should be float32, got {spec.PL.dtype}"
        assert isinstance(spec.PLB, np.ndarray), f"PLB should be ndarray, got {type(spec.PLB)}"
        assert spec.PLB.dtype == np.float32, f"PLB dtype should be float32, got {spec.PLB.dtype}"
        assert isinstance(spec.WL, np.ndarray), f"WL should be ndarray, got {type(spec.WL)}"
        assert spec.WL.dtype == np.float32, f"WL dtype should be float32, got {spec.WL.dtype}"
        assert isinstance(spec.BG, np.ndarray), f"BG should be ndarray, got {type(spec.BG)}"
        assert spec.BG.dtype == np.float32, f"BG dtype should be float32, got {spec.BG.dtype}"

        expected_plb = (pl_vals - bg_vals).astype(np.float32)
        assert np.allclose(spec.PLB, expected_plb, rtol=1e-5), "PLB values incorrect"

        print("  (tkinter tests): PL, PLB, WL, BG are float32")
    finally:
        os.unlink(fname)


def test_spectrumdata_loadeachbg_float32():
    """Test that SpectrumData stores BG as float32 when loadeachbg=True."""
    if not HAS_TKINTER:
        print("  (skipped: tkinter not available)")
        return

    import lib9 as lib

    n = 50
    wl_vals = np.linspace(450.0, 700.0, n)
    bg_vals = np.full(n, 150)
    pl_vals = np.random.randint(300, 6000, n)

    fname = create_mock_spectrum_file(wl_vals, bg_vals, pl_vals)
    try:
        shared_wl = np.array(wl_vals, dtype=np.float32)
        spec = lib.SpectrumData(
            filename=fname, WL=shared_wl, BG=[], loadeachbg=True,
        )

        assert spec.dataokay, "SpectrumData should be OK"
        assert isinstance(spec.BG, np.ndarray), f"BG should be ndarray, got {type(spec.BG)}"
        assert spec.BG.dtype == np.float32, f"BG dtype should be float32, got {spec.BG.dtype}"
        assert isinstance(spec.PLB, np.ndarray), f"PLB should be ndarray, got {type(spec.PLB)}"
        assert spec.PLB.dtype == np.float32, f"PLB dtype should be float32, got {spec.PLB.dtype}"

        print("  (tkinter tests loadeachbg): BG and PLB are float32")
    finally:
        os.unlink(fname)


def test_derivatives_float32():
    """Test that normalized derivative arrays are stored as float32."""
    import hsi_normalization

    class MockSpec:
        def __init__(self):
            n = 100
            self.WL = np.linspace(450.0, 700.0, n, dtype=np.float32)
            self.PLB = np.random.rand(n).astype(np.float32) * 1000
            self.Specdiff1 = None
            self.Specdiff2 = None
            self.dataokay = True

    spec = MockSpec()
    n = len(spec.PLB)
    spec.Specdiff1 = np.zeros(n, dtype=np.float32)
    spec.Specdiff2 = np.zeros(n, dtype=np.float32)
    spec.Specdiff1[:] = np.gradient(spec.PLB, spec.WL)
    spec.Specdiff2[:] = np.gradient(spec.Specdiff1, spec.WL)

    matrix = [[spec]]
    hsi_normalization.normalize_derivatives_by_signal(matrix, signal_key='PLB')

    assert hasattr(spec, 'Specdiff1_norm'), "Specdiff1_norm should be set"
    assert hasattr(spec, 'Specdiff2_norm'), "Specdiff2_norm should be set"
    assert spec.Specdiff1_norm.dtype == np.float32, \
        f"Specdiff1_norm dtype should be float32, got {spec.Specdiff1_norm.dtype}"
    assert spec.Specdiff2_norm.dtype == np.float32, \
        f"Specdiff2_norm dtype should be float32, got {spec.Specdiff2_norm.dtype}"
    print("  normalize_derivatives_by_signal: Specdiff1_norm and Specdiff2_norm are float32")


def test_xymap_wl_bg_float32():
    """Test that XYMap.loadfiles() stores WL and BG as float32."""
    if not HAS_TKINTER:
        print("  (skipped: tkinter not available)")
        return

    import lib9 as lib

    n = 50
    wl_vals = np.linspace(450.0, 700.0, n)
    bg_vals = np.full(n, 80)
    pl_vals = np.random.randint(200, 5000, n)

    fnames = [create_mock_spectrum_file(wl_vals, bg_vals, pl_vals) for _ in range(4)]

    try:
        xymap = lib.XYMap(fnames=fnames, cmapframe=None, specframe=None, skip_gui_build=True)

        assert isinstance(xymap.WL, np.ndarray), f"XYMap.WL should be ndarray"
        assert xymap.WL.dtype == np.float32, f"XYMap.WL dtype should be float32, got {xymap.WL.dtype}"
        assert isinstance(xymap.BG, np.ndarray), f"XYMap.BG should be ndarray"
        assert xymap.BG.dtype == np.float32, f"XYMap.BG dtype should be float32, got {xymap.BG.dtype}"
        assert isinstance(xymap.WL_eV, np.ndarray), f"XYMap.WL_eV should be ndarray"
        assert 400.0 < float(xymap.WL[0]) < 800.0, f"WL should be in nm range, got {xymap.WL[0]}"

        for spec in xymap.specs:
            if spec is not None:
                assert spec.WL.dtype == np.float32, f"spec.WL dtype should be float32"
                assert spec.PLB.dtype == np.float32, f"spec.PLB dtype should be float32"
                assert spec.PL.dtype == np.float32, f"spec.PL dtype should be float32"

        print(f"  XYMap.loadfiles(): WL, BG, per-spec WL/PLB/PL are float32")
    finally:
        for fname in fnames:
            os.unlink(fname)


if __name__ == '__main__':
    print("=" * 60)
    print("Test: Float32 storage for SpectrumData arrays")
    print("=" * 60)

    tests = [
        ("SpectrumData float32 (loadeachbg=False)", test_spectrumdata_float32),
        ("SpectrumData float32 (loadeachbg=True)", test_spectrumdata_loadeachbg_float32),
        ("normalize_derivatives_by_signal float32", test_derivatives_float32),
        ("XYMap WL/BG float32", test_xymap_wl_bg_float32),
    ]

    passed = 0
    failed = 0
    for name, test in tests:
        print(f"\n{name}:")
        try:
            test()
            passed += 1
            print(f"  PASS")
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    if failed == 0:
        print(f"All {passed} tests PASSED!")
    else:
        print(f"{failed} tests FAILED, {passed} PASSED")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
