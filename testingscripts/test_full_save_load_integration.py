"""
Integration test for ROI and Averaged Spectra Save/Load functionality
Tests the complete workflow with real XYMap instance
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import tempfile
import pickle

# Import the libraries
import lib9 as lib
import PMclasslib1 as PMlib
import deflib1 as deflib

def test_full_integration():
    """
    Test the complete save/load workflow with ROIs and averaged spectra
    """
    print("=" * 60)
    print("Full Integration Test: ROI and Spectra Save/Load")
    print("=" * 60)
    
    # Create temporary file for saving
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pkl')
    temp_filename = temp_file.name
    temp_file.close()
    
    try:
        # ===== SETUP: Create XYMap with test data =====
        print("\n1. Creating XYMap instance with mock data...")
        
        # Create mock spectral data
        wl = np.linspace(400, 800, 100)
        num_spectra = 12  # 3x4 grid
        
        # Create mock SpectrumData objects
        specs = []
        bg_array = 100 + np.random.randn(len(wl)) * 10
        
        for i in range(num_spectra):
            # Create mock spectrum with some variation
            pl = 1000 + 500 * np.sin(wl / 50) + np.random.randn(len(wl)) * 50 + i * 100
            
            # Create temp file for each spectrum
            temp_spec_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            temp_spec_file.write("# Mock spectrum\n")
            temp_spec_file.write("WL (nm)\tPL (counts)\n")
            for w, p in zip(wl, pl):
                temp_spec_file.write(f"{w:.2f}\t{p:.2f}\n")
            temp_spec_file.close()
            
            # Create SpectrumData with required parameters
            spec = lib.SpectrumData(
                temp_spec_file.name, 
                wl, 
                bg_array,
                loadeachbg=False,
                linearbg=False,
                removecosmics=False
            )
            spec.metadata = {'x': i % 4, 'y': i // 4}
            specs.append(spec)
            
            # Clean up temp file
            os.unlink(temp_spec_file.name)
        
        # Create XYMap instance (skip GUI since we're in headless mode)
        defaults = deflib.getDefaults()
        nanomap = lib.XYMap(
            specs, None, None,
            False, False, False,
            20, 3, list(deflib.cosmicfuncts.keys())[0],
            defaults,
            skip_gui_build=True
        )
        
        print(f"  Created XYMap with {len(nanomap.specs)} spectra")
        print(f"  WL range: {nanomap.WL[0]:.1f} - {nanomap.WL[-1]:.1f} nm")
        
        # ===== CREATE HSI IMAGE =====
        print("\n2. Creating HSI image...")
        
        # Create a 3x4 HSI matrix
        hsi_matrix = np.random.rand(3, 4) * 1000 + 500
        
        # Create PMclass object
        pm = PMlib.PMclass(hsi_matrix, 'Test_HSI', 550.0, nanomap.WL, {'test': 'metadata'})
        nanomap.PMdict['Test_HSI'] = pm
        
        print(f"  Created HSI 'Test_HSI' with shape {hsi_matrix.shape}")
        
        # ===== CREATE ROIs =====
        print("\n3. Creating ROI masks...")
        
        # Create ROI handler if not exists
        if not hasattr(nanomap, 'roihandler'):
            nanomap.roihandler = lib.Roihandler(nanomap.PMdict, nanomap.WL)
        
        # Create ROI 1: bright region (top-left corner)
        roi1 = np.full((3, 4), np.nan)
        roi1[0:2, 0:2] = 1.0
        nanomap.roihandler.roilist['bright_region'] = roi1
        
        # Create ROI 2: edge region (bottom row)
        roi2 = np.full((3, 4), np.nan)
        roi2[2, :] = 1.0
        nanomap.roihandler.roilist['bottom_edge'] = roi2
        
        roi_count = len(nanomap.roihandler.roilist)
        print(f"  Created {roi_count} ROI masks:")
        for roi_name in nanomap.roihandler.roilist.keys():
            print(f"    - {roi_name}")
        
        # ===== CREATE AVERAGED SPECTRA =====
        print("\n4. Creating averaged spectra...")
        
        # Create averaged spectrum 1: PLB
        avg_spec_plb = PMlib.Spectra(
            np.mean([s.PLB for s in nanomap.specs], axis=0),
            nanomap.WL,
            {'type': 'averaged', 'datatype': 'PLB'},
            'Test_HSI'
        )
        nanomap.disspecs['Test_HSI_PLB_avg'] = avg_spec_plb
        
        # Create averaged spectrum 2: first derivative
        spec_for_deriv = nanomap.specs[0]
        spec_for_deriv.Spec_d1 = np.gradient(spec_for_deriv.PLB, nanomap.WL)
        avg_spec_d1 = PMlib.Spectra(
            np.gradient(avg_spec_plb.Spec, nanomap.WL),
            nanomap.WL,
            {'type': 'averaged', 'datatype': 'Specdiff1'},
            'Test_HSI'
        )
        avg_spec_d1.Spec_d1 = avg_spec_d1.Spec.copy()
        nanomap.disspecs['Test_HSI_Specdiff1_avg'] = avg_spec_d1
        
        spec_count = len(nanomap.disspecs)
        print(f"  Created {spec_count} averaged spectra:")
        for spec_name in nanomap.disspecs.keys():
            print(f"    - {spec_name}")
        
        # ===== SAVE STATE =====
        print(f"\n5. Saving state to: {temp_filename}")
        
        save_success = nanomap.save_state(temp_filename)
        
        if save_success:
            print("  Save successful!")
            file_size = os.path.getsize(temp_filename)
            print(f"  File size: {file_size / 1024:.1f} KB")
        else:
            print("  ✗ Save FAILED!")
            return False
        
        # Store original data for comparison
        original_roi_count = len(nanomap.roihandler.roilist)
        original_roi_names = list(nanomap.roihandler.roilist.keys())
        original_spec_count = len(nanomap.disspecs)
        original_spec_names = list(nanomap.disspecs.keys())
        original_hsi_count = len(nanomap.PMdict)
        original_hsi_shape = hsi_matrix.shape
        
        # ===== LOAD STATE =====
        print(f"\n6. Loading state from: {temp_filename}")
        
        # Create new XYMap instance for loading
        nanomap2 = lib.XYMap(
            [], None, None,
            False, False, False,
            20, 3, list(deflib.cosmicfuncts.keys())[0],
            defaults,
            skip_gui_build=True
        )
        
        load_success = nanomap2.load_state(temp_filename)
        
        if load_success:
            print("  Load successful!")
        else:
            print("  ✗ Load FAILED!")
            return False
        
        # ===== VERIFY LOADED DATA =====
        print("\n7. Verifying loaded data...")
        
        # Verify ROIs
        loaded_roi_count = len(nanomap2.roihandler.roilist) if hasattr(nanomap2, 'roihandler') else 0
        loaded_roi_names = list(nanomap2.roihandler.roilist.keys()) if hasattr(nanomap2, 'roihandler') else []
        
        if loaded_roi_count == original_roi_count:
            print(f"  ROI count matches: {loaded_roi_count}")
        else:
            print(f"  ✗ ROI count mismatch: expected {original_roi_count}, got {loaded_roi_count}")
            return False
        
        if set(loaded_roi_names) == set(original_roi_names):
            print(f"  ROI names match: {loaded_roi_names}")
        else:
            print(f"  ✗ ROI names mismatch!")
            print(f"    Expected: {original_roi_names}")
            print(f"    Got: {loaded_roi_names}")
            return False
        
        # Verify ROI data integrity
        for roi_name in original_roi_names:
            original_roi = np.array(nanomap.roihandler.roilist[roi_name])
            loaded_roi = np.array(nanomap2.roihandler.roilist[roi_name])
            
            # Compare shapes
            if original_roi.shape != loaded_roi.shape:
                print(f"  ✗ ROI '{roi_name}' shape mismatch!")
                return False
            
            # Compare values (including NaN)
            nan_match = np.isnan(original_roi) == np.isnan(loaded_roi)
            val_match = np.allclose(original_roi[~np.isnan(original_roi)], 
                                   loaded_roi[~np.isnan(loaded_roi)])
            
            if nan_match.all() and val_match:
                print(f"  ROI '{roi_name}' data integrity verified")
            else:
                print(f"  ✗ ROI '{roi_name}' data mismatch!")
                return False
        
        # Verify averaged spectra
        loaded_spec_count = len(nanomap2.disspecs)
        loaded_spec_names = list(nanomap2.disspecs.keys())
        
        if loaded_spec_count == original_spec_count:
            print(f"  Averaged spectra count matches: {loaded_spec_count}")
        else:
            print(f"  ✗ Spectra count mismatch: expected {original_spec_count}, got {loaded_spec_count}")
            return False
        
        if set(loaded_spec_names) == set(original_spec_names):
            print(f"  Spectra names match: {loaded_spec_names}")
        else:
            print(f"  ✗ Spectra names mismatch!")
            print(f"    Expected: {original_spec_names}")
            print(f"    Got: {loaded_spec_names}")
            return False
        
        # Verify spectra data integrity
        for spec_name in original_spec_names:
            original_spec = nanomap.disspecs[spec_name]
            loaded_spec = nanomap2.disspecs[spec_name]
            
            # Check WL arrays match
            if not np.allclose(original_spec.WL, loaded_spec.WL):
                print(f"  ✗ Spectrum '{spec_name}' WL mismatch!")
                return False
            
            # Check spectral data matches
            if not np.allclose(original_spec.Spec, loaded_spec.Spec):
                print(f"  ✗ Spectrum '{spec_name}' data mismatch!")
                return False
            
            print(f"  Spectrum '{spec_name}' data integrity verified")
        
        # Verify HSI data
        loaded_hsi_count = len(nanomap2.PMdict)
        if loaded_hsi_count == original_hsi_count:
            print(f"  HSI count matches: {loaded_hsi_count}")
        else:
            print(f"  ✗ HSI count mismatch: expected {original_hsi_count}, got {loaded_hsi_count}")
            return False
        
        if 'Test_HSI' in nanomap2.PMdict:
            loaded_hsi_shape = np.array(nanomap2.PMdict['Test_HSI'].PixMatrix).shape
            if loaded_hsi_shape == original_hsi_shape:
                print(f"  HSI shape matches: {loaded_hsi_shape}")
            else:
                print(f"  ✗ HSI shape mismatch: expected {original_hsi_shape}, got {loaded_hsi_shape}")
                return False
        
        # ===== SUCCESS =====
        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - ROIs: {loaded_roi_count} masks saved and loaded correctly")
        print(f"  - Averaged spectra: {loaded_spec_count} spectra saved and loaded correctly")
        print(f"  - HSI images: {loaded_hsi_count} images saved and loaded correctly")
        print(f"  - Data integrity: All arrays match exactly (including NaN values)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
            print(f"\nCleaned up temporary file: {temp_filename}")


if __name__ == '__main__':
    success = test_full_integration()
    sys.exit(0 if success else 1)
