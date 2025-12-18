import tkinter as tk
from tkinter import ttk
import numpy as np
import sys
import os

# Mock classes to simulate lib9.py environment
class MockSpectrumData:
    def __init__(self, wl, plb):
        self.WL = wl
        self.PLB = plb
        self.Specdiff1 = []
        self.Specdiff2 = []

class MockXYMap:
    def __init__(self, derivative_polynomarray):
        self.derivative_polynomarray = derivative_polynomarray
        self.specs = []
    
    def calculate_derivatives(self):
        """
        Copy of the calculate_derivatives method from lib9.py (with the fix I applied earlier)
        """
        # Check if derivative calculation is requested
        # derivative_polynomarray: [first_derivative_bool, second_derivative_bool, polynomial_order, N_fitpoints]
        if not self.derivative_polynomarray or len(self.derivative_polynomarray) < 4:
            print("Error: derivative_polynomarray is invalid")
            return

        try:
            calc_d1 = self.derivative_polynomarray[0].get()
            calc_d2 = self.derivative_polynomarray[1].get()
            print(f"Flags: d1={calc_d1}, d2={calc_d2}")
        except Exception as e:
            print(f"Error getting flags: {e}")
            return
        
        if not (calc_d1 or calc_d2):
            print("Neither d1 nor d2 requested.")
            return

        try:
            poly_order = int(self.derivative_polynomarray[2].get())
            N_fitpoints = int(self.derivative_polynomarray[3].get())
            print(f"Params: order={poly_order}, window={N_fitpoints}")
        except (ValueError, TypeError) as e:
            print(f"Invalid polynomial order or fit points: {e}")
            return

        if N_fitpoints % 2 == 0:
            N_fitpoints += 1 # Ensure odd window size

        print(f"Calculating derivatives: d1={calc_d1}, d2={calc_d2}, order={poly_order}, window={N_fitpoints}")

        # Iterate over all spectra
        for i, spec in enumerate(self.specs):
            if spec is None:
                continue
                
            # Ensure we have data
            if spec.PLB is None or spec.WL is None or len(spec.PLB) == 0 or len(spec.WL) == 0 or len(spec.PLB) != len(spec.WL):
                print(f"Spec {i}: Invalid data")
                continue

            wl = np.array(spec.WL)
            plb = np.array(spec.PLB)
            
            # Initialize derivative arrays with zeros
            if calc_d1:
                spec.Specdiff1 = np.zeros_like(plb)
            if calc_d2:
                spec.Specdiff2 = np.zeros_like(plb)

            half_window = N_fitpoints // 2
            n_points = len(wl)

            # Sliding window loop
            for i in range(half_window, n_points - half_window):
                start_idx = i - half_window
                end_idx = i + half_window + 1
                
                # Extract window
                wl_window = wl[start_idx:end_idx]
                plb_window = plb[start_idx:end_idx]
                
                # Fit polynomial
                try:
                    p = np.polyfit(wl_window, plb_window, poly_order)
                    
                    if calc_d1:
                        # First derivative
                        dp = np.polyder(p)
                        spec.Specdiff1[i] = np.polyval(dp, wl[i])
                        
                    if calc_d2:
                        # Second derivative
                        ddp = np.polyder(np.polyder(p))
                        spec.Specdiff2[i] = np.polyval(ddp, wl[i])
                        
                except Exception as e:
                    print(f"Fit error at index {i}: {e}")
                    pass

def main():
    root = tk.Tk() # Needed for Tkinter variables
    
    # Mock Tkinter variables as used in main9.py
    calculate_firstderivativeBool = tk.IntVar()
    calculate_firstderivativeBool.set(1) # Set to True
    
    calculate_secondderivativeBool = tk.IntVar()
    calculate_secondderivativeBool.set(1) # Set to True
    
    derivative_polyorder_entry = ttk.Combobox(root, values=[1, 2, 3, 4, 5])
    derivative_polyorder_entry.insert(0, "2")
    
    derivative_fitpoints_entry = tk.Entry(root)
    derivative_fitpoints_entry.insert(0, "15")
    
    derivative_polynomarray = [
        calculate_firstderivativeBool,
        calculate_secondderivativeBool,
        derivative_polyorder_entry,
        derivative_fitpoints_entry
    ]
    
    # Create Mock Data
    wl = np.linspace(400, 800, 100)
    plb = np.sin(wl/50) # Simple sine wave
    
    spec = MockSpectrumData(wl, plb)
    
    # Create Mock XYMap
    xymap = MockXYMap(derivative_polynomarray)
    xymap.specs.append(spec)
    
    # Run calculation
    print("--- Starting Calculation ---")
    xymap.calculate_derivatives()
    print("--- Calculation Finished ---")
    
    # Check results
    print(f"Specdiff1 length: {len(spec.Specdiff1)}")
    print(f"Specdiff2 length: {len(spec.Specdiff2)}")
    
    if len(spec.Specdiff1) > 0:
        print(f"Specdiff1 sample: {spec.Specdiff1[50]}")
        if np.all(spec.Specdiff1 == 0):
            print("WARNING: Specdiff1 is all zeros!")
    else:
        print("WARNING: Specdiff1 is empty list!")

    if len(spec.Specdiff2) > 0:
        print(f"Specdiff2 sample: {spec.Specdiff2[50]}")
        if np.all(spec.Specdiff2 == 0):
            print("WARNING: Specdiff2 is all zeros!")
    else:
        print("WARNING: Specdiff2 is empty list!")

if __name__ == "__main__":
    main()
