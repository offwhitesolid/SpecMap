# PMclasslib1.py: calc_derivative Documentation

## Overview
The `calc_derivative` method in the `Spectra` class of `PMclasslib1.py` calculates the first and second derivatives of a spectrum using a sliding window polynomial fitting approach (Savitzky-Golay like method).

## Method Signature
```python
def calc_derivative(self, derivative_polynomarray):
```

## Parameters
- **derivative_polynomarray** (`list`): A list containing configuration parameters for the derivative calculation.
    - `index 0` (`bool`): `first_derivative_bool` - If `True`, calculate the first derivative.
    - `index 1` (`bool`): `second_derivative_bool` - If `True`, calculate the second derivative.
    - `index 2` (`int`): `polynomial_order` - The order of the polynomial to fit (e.g., 2 or 3).
    - `index 3` (`int`): `N_fitpoints` - The size of the sliding window (number of points). Should be an odd number.

## Algorithm Description
The method iterates through each point in the spectrum (wavelength array `WL` and intensity array `Spec`). For each point:
1.  It defines a window of size `N_fitpoints` centered at the current point.
2.  It fits a polynomial of order `polynomial_order` to the data within this window using `numpy.polyfit`.
3.  It calculates the analytical derivative of the fitted polynomial using `numpy.polyder`.
4.  It evaluates the derivative polynomial at the current wavelength `WL[i]` using `numpy.polyval`.

This approach provides a smoothed derivative, reducing the noise amplification inherent in finite difference methods.

## Outputs
The method sets the following attributes on the `Spectra` instance:
- **self.Spec_d1** (`numpy.ndarray`): The first derivative of the spectrum (if requested).
- **self.Spec_d2** (`numpy.ndarray`): The second derivative of the spectrum (if requested).

## Example Usage
```python
import PMclasslib1

# Create a Spectra object
# spec = PMclasslib1.Spectra(...)

# Configuration: Calculate both derivatives, 2nd order poly, 7 point window
config = [True, True, 2, 7] 

# Calculate derivatives (passing the spectra object as the first argument)
PMclasslib1.calc_derivative(spec, config)

# Access results
first_deriv = spec.Spec_d1
second_deriv = spec.Spec_d2
```
