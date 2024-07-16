import numpy as np
from scipy.optimize import curve_fit
from scipy.special import wofz
from scipy.optimize import fminbound

# window functions

def double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2):
    return voigtwind(x, amp1, cen1, wid1, gamma1) + voigtwind(x, amp2, cen2, wid2, gamma2)

def double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2):
    return gaussianwind(x, amp1, cen1, wid1) + gaussianwind(x, amp2, cen2, wid2)

def double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2):
    return lorentzwind(x, amp1, cen1, wid1) + lorentzwind(x, amp2, cen2, wid2)

def gaussianwind(x, amp, cen, wid):
    return amp * np.exp(-(x - cen)**2 / (2 * wid**2))

def lorentzwind(x, amp, cen, wid):
    return amp / (1 + (x - cen)**2 / wid**2)

def voigtwind(x, amp, cen, wid, gamma):
    return amp * np.real(wofz(((x - cen) + 1j*gamma) / wid / np.sqrt(2))) / wid / np.sqrt(2*np.pi)

def linearwind(x, a, b):
    return np.multiply(a, x) + b

# fit window functions to data  

def fitdoublegaussiantospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(double_gaussianwind, x, y, p0=initialguess, maxfev=maxfev)
    amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit, pcov

def fitdoublelorentztospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(double_lorentzwind, x, y, p0=initialguess, maxfev=maxfev)
    amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit, pcov

def fitdoublevoigttospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.std(x), np.max(y), x[np.argmax(y)], np.std(x), np.std(x)]
    fitdata, pcov = curve_fit(double_voigtwind, x, y, p0=initialguess, maxfev=maxfev)
    amp1_fit, cen1_fit, wid1_fit, gamma1_fit, amp2_fit, cen2_fit, wid2_fit, gamma2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, gamma1_fit, amp2_fit, cen2_fit, wid2_fit, gamma2_fit, pcov

def fitvoigttospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.std(x)]
    fitdata, pcov = curve_fit(voigtwind, x, y, p0=initialguess, maxfev=maxfev)
    amp_fit, cen_fit, wid_fit, gamma_fit = fitdata
    return amp_fit, cen_fit, wid_fit, gamma_fit, pcov

def fitlorentztospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(lorentzwind, x, y, p0=initialguess, maxfev=maxfev)
    amp_fit, cen_fit, wid_fit = fitdata
    return amp_fit, cen_fit, wid_fit, pcov

def fitgaussiantospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(gaussianwind, x, y, p0=initialguess, maxfev=maxfev)
    amp_fit, cen_fit, wid_fit = fitdata
    return amp_fit, cen_fit, wid_fit, pcov
    
def fitlinetospec(start, end, WL, PLB, maxfev=10000):
    x = WL[start: end]
    y = PLB[start: end]
    a_guess = (np.max(y) - np.min(y)) / (np.max(x) - np.min(x))
    b_guess = np.mean(y) - a_guess * np.mean(x)
    initial_guess = [a_guess, b_guess]
    fitdata, pconf = curve_fit(linearwind, x, y, p0=initial_guess, maxfev=maxfev)
    a, b = fitdata
    return a, b, pconf

# get maxima of fitted functions

def getmaxdoublegaussian(amp1, cen1, wid1, amp2, cen2, wid2):
    # Define the fitted function
    fitted_func = lambda x: -double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2)
    # Initial guess for the maximum
    x0 = [cen1, cen2]
    # Find the maximum of the fitted function
    x_max = fminbound(lambda x: -fitted_func(x), np.min(x0), np.max(x0))
    return -fitted_func(x_max), x_max

def getmaxdoublelorentz(amp1, cen1, wid1, amp2, cen2, wid2):
    # Define the fitted function
    fitted_func = lambda x: -double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2)
    # Initial guess for the maximum
    x0 = [cen1, cen2]
    # Find the maximum of the fitted function
    x_max = fminbound(lambda x: -fitted_func(x), np.min(x0), np.max(x0))
    return -fitted_func(x_max), x_max

def getmaxdoublevoigt(amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2):
    # Define the fitted function
    fitted_func = lambda x: -double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2)
    # Initial guess for the maximum
    x0 = [cen1, cen2]
    # Find the maximum of the fitted function
    x_max = fminbound(lambda x: -fitted_func(x), np.min(x0), np.max(x0))
    return -fitted_func(x_max), x_max

def getmaxgaussian(amp, cen, wid):
    # Define the fitted function
    fitted_func = lambda x: -gaussianwind(x, amp, cen, wid)
    # Initial guess for the maximum
    x0 = cen
    # Find the maximum of the fitted function
    x_max = fminbound(lambda x: -fitted_func(x), np.min(x0), np.max(x0))
    return -fitted_func(x_max), x_max

def getmaxlorentz(amp, cen, wid):
    # Define the fitted function
    fitted_func = lambda x: -lorentzwind(x, amp, cen, wid)
    # Initial guess for the maximum
    x0 = cen
    # Find the maximum of the fitted function
    x_max = fminbound(lambda x: -fitted_func(x), np.min(x0), np.max(x0))
    return -fitted_func(x_max), x_max

def getmaxvoigt(amp, cen, wid, gamma):
    # Define the fitted function
    fitted_func = lambda x: -voigtwind(x, amp, cen, wid, gamma)
    # Initial guess for the maximum
    x0 = cen
    # Find the maximum of the fitted function
    x_max = fminbound(lambda x: -fitted_func(x), np.min(x0), np.max(x0))
    return -fitted_func(x_max), x_max

def getmaxlinear(a, b):
    pass

def gaussian2d(coords, *params):
    x, y = coords
    amp, cenx, ceny, sigmax, sigmay, theta = params
    a = (np.cos(theta)**2) / (2 * sigmax**2) + (np.sin(theta)**2) / (2 * sigmay**2)
    b = -(np.sin(2 * theta)) / (4 * sigmax**2) + (np.sin(2 * theta)) / (4 * sigmay**2)
    c = (np.sin(theta)**2) / (2 * sigmax**2) + (np.cos(theta)**2) / (2 * sigmay**2)
    return amp * np.exp(-(a * (x - cenx)**2 + 2 * b * (x - cenx) * (y - ceny) + c * (y - ceny)**2))

def fitgaussiand2dtomatrix(inpdata, maxfev=10000):
    data = np.array(inpdata)
    x = np.arange(data.shape[1])
    y = np.arange(data.shape[0])
    x, y = np.meshgrid(x, y)
    # Include an initial guess for theta as well, e.g., 0
    initialguess = [np.max(data), np.argmax(data) % data.shape[1], np.argmax(data) // data.shape[1], 1, 1, 0]
    fitdata, pcov = curve_fit(gaussian2d, (x, y), data.ravel(), p0=initialguess, maxfev=maxfev)
    fwhmx = 2 * np.sqrt(2 * np.log(2)) * fitdata[3]
    fwhmy = 2 * np.sqrt(2 * np.log(2)) * fitdata[4]
    return fitdata, pcov, fwhmx, fwhmy

def Newtonmax(f, x0, tol=1e-6, maxiter=10000):
    # Initialize the iteration counter
    iter = 0
    # Initialize the error
    error = tol + 1
    # Iterate until the error is less than the tolerance or the maximum number of iterations is reached
    while error > tol and iter < maxiter:
        # Calculate the derivative of the function at the current point
        f_prime = (f(x0 + tol) - f(x0 - tol)) / (2 * tol)
        # Calculate the next point using Newton's method
        x1 = x0 - f(x0) / f_prime
        # Calculate the error
        error = np.abs(x1 - x0)
        # Update the current point
        x0 = x1
        # Increment the iteration counter
        iter += 1
    return x0

# dictionary of window functions and their corresponding fit functions
# and functions to get the maxima of the fitted functions
# key: window function name
# value: list of window function, fit function, and function to get maxima of the fit function
fitkeys = {'lorentz':[lorentzwind, fitlorentztospec, getmaxlorentz, 'Lorentz fit'],
           'gaussian':[gaussianwind, fitgaussiantospec, getmaxgaussian, 'Gaussian fit'], 
           'voigt':[voigtwind, fitvoigttospec, getmaxvoigt, 'Voigt fit'], 
           'linear':[linearwind, fitlinetospec, getmaxlinear, 'Linear fit'], 
           'double lorentz':[double_lorentzwind, fitdoublelorentztospec, getmaxdoublelorentz, 'Double Lorentz fit'], 
           'double gaussian':[double_gaussianwind, fitdoublegaussiantospec, getmaxdoublegaussian, 'Double Gaussian fit'], 
           'double voigt':[double_voigtwind, fitdoublevoigttospec, getmaxdoublevoigt, 'Double Voigt fit']}

