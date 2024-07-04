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

def fitdoublegaussiantospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(double_gaussianwind, x, y, p0=initialguess, maxfev=10000)
    amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit, pcov

def fitdoublelorentztospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(double_lorentzwind, x, y, p0=initialguess, maxfev=10000)
    amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit, pcov

def fitdoublevoigttospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.std(x), np.max(y), x[np.argmax(y)], np.std(x), np.std(x)]
    fitdata, pcov = curve_fit(double_voigtwind, x, y, p0=initialguess, maxfev=10000)
    amp1_fit, cen1_fit, wid1_fit, gamma1_fit, amp2_fit, cen2_fit, wid2_fit, gamma2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, gamma1_fit, amp2_fit, cen2_fit, wid2_fit, gamma2_fit, pcov

def fitvoigttospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x), np.std(x)]
    fitdata, pcov = curve_fit(voigtwind, x, y, p0=initialguess, maxfev=10000)
    amp_fit, cen_fit, wid_fit, gamma_fit = fitdata
    return amp_fit, cen_fit, wid_fit, gamma_fit, pcov

def fitlorentztospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(lorentzwind, x, y, p0=initialguess, maxfev=10000)
    amp_fit, cen_fit, wid_fit = fitdata
    return amp_fit, cen_fit, wid_fit, pcov

def fitgaussiantospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    initialguess = [np.max(y), x[np.argmax(y)], np.std(x)]
    fitdata, pcov = curve_fit(gaussianwind, x, y, p0=initialguess, maxfev=10000)
    amp_fit, cen_fit, wid_fit = fitdata
    return amp_fit, cen_fit, wid_fit, pcov
    
def fitlinetospec(start, end, WL, PLB):
    x = WL[start: end]
    y = PLB[start: end]
    a_guess = (np.max(y) - np.min(y)) / (np.max(x) - np.min(x))
    b_guess = np.mean(y) - a_guess * np.mean(x)
    initial_guess = [a_guess, b_guess]
    fitdata, pconf = curve_fit(linearwind, x, y, p0=initial_guess, maxfev=10000)
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

