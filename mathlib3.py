import numpy as np
from scipy.optimize import curve_fit, minimize
from scipy.special import wofz
from scipy.optimize import fminbound
from scipy.special import jv
from scipy.signal import find_peaks
from scipy.signal import savgol_filter
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt

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

def voigtwindapprox(x, anp, cen, sig, gam):
    # returns the pseudo-voigt provile as a sum of gaussian and lorentzian profiles
    return anp * (1 - gam / (2 * sig) * np.sqrt(2 * np.pi) * np.exp(-2 * np.log(2) * ((x - cen) / sig)**2) + (1 - gam) / np.pi / sig / (1 + ((x - cen) / sig)**2))

# def voigtwind(x, amp, cen, wid, gamma): old version
#    return amp * np.real(wofz(((x - cen) + 1j*gamma) / wid / np.sqrt(2))) / wid / np.sqrt(2*np.pi)

def voigtwind_complex(x, amp, cen, wid, gamma):
    sigma = wid / np.sqrt(2 * np.log(2))  # Convert FWHM to standard deviation
    z = ((x - cen) + 1j * gamma) / (sigma * np.sqrt(2))
    return amp * np.real(wofz(z)) / (sigma * np.sqrt(2 * np.pi))

# pseudo-voigt function for faster fitting
def voigtwind(x, amp, cen, fwhm, eta):
    sigma = fwhm / 2.354820045
    gamma = fwhm / 2.0
    G = np.exp(-0.5*((x-cen)/sigma)**2)
    L = gamma**2 / ((x-cen)**2 + gamma**2)
    return amp * (eta*L + (1-eta)*G)

def linearwind(x, a, b):
    return np.multiply(a, x) + b

# estimate initial parameters for fitting functions

def estimate_voigt_params(x, y):
    """
    Estimate good starting values for fitting a Voigt profile.
    
    Parameters:
    - x: Array of x values.
    - y: Array of y values.
    
    Returns:
    - amp_init: Estimated amplitude of the Voigt peak.
    - cen_init: Estimated center (location) of the Voigt peak.
    - wid_init: Estimated width (FWHM) of the Voigt peak.
    - gamma_init: Estimated Lorentzian width (gamma), set to a small value initially.
    """
    # Estimate amplitude as the max value of y
    amp_init = np.max(y)
    
    # Estimate center as the x value where y is maximum
    cen_init = x[np.argmax(y)]
    
    # Estimate FWHM (Full Width at Half Maximum)
    half_max = amp_init / 2
    
    # Find where y crosses half_max to calculate the width
    left_idx = np.where(y > half_max)[0][0]  # First index where y > half max
    right_idx = np.where(y > half_max)[0][-1]  # Last index where y > half max
    fwhm = x[right_idx] - x[left_idx]  # Approximate FWHM as width
    
    # Set initial width (wid) as the FWHM
    wid_init = fwhm
    
    # Set an initial small value for gamma
    gamma_init = 0.1  # You can adjust this based on data
    
    return amp_init, cen_init, wid_init, gamma_init

def estimate_double_voigt_params(x, y):
    """
    Estimate good starting values for fitting a double Voigt profile.
    
    Parameters:
    - x: Array of x values.
    - y: Array of y values.
    
    Returns:
    - amp_init: List of estimated amplitudes for the two Voigt peaks.
    - cen_init: List of estimated centers (locations) for the two Voigt peaks.
    - wid_init: List of estimated widths (FWHM) for the two Voigt peaks.
    - gamma_init: List of estimated Lorentzian widths (gamma) for both peaks.
    """
    # Find two prominent peaks in the data
    peaks, _ = find_peaks(y, height=0.1, distance=10)  # Adjust height and distance if needed
    
    if len(peaks) < 2:
        raise ValueError("Less than two peaks found in the data. Make sure the data contains two distinct peaks.")

    # Sort the peaks by prominence (highest peaks first)
    sorted_peaks = peaks[np.argsort(y[peaks])][::-1]  # Sort peaks by height, highest first
    
    amp_init = []
    cen_init = []
    wid_init = []
    gamma_init = []

    # Estimate parameters for each peak
    for peak_idx in sorted_peaks[:2]:  # Only consider the top 2 peaks
        amp = y[peak_idx]  # Amplitude is the peak height
        cen = x[peak_idx]  # Center is the x-value at the peak

        # Estimate FWHM (Full Width at Half Maximum)
        half_max = amp / 2
        left_idx = np.where(y > half_max)[0][0]  # First index where y > half max
        right_idx = np.where(y > half_max)[0][-1]  # Last index where y > half max
        fwhm = x[right_idx] - x[left_idx]  # Approximate FWHM as width

        # Set initial values for this peak
        amp_init.append(amp)
        cen_init.append(cen)
        wid_init.append(fwhm)
        gamma_init.append(0.1)  # Small initial value for gamma
    
    return amp_init[0], cen_init[0], wid_init[0], gamma_init[0], amp_init[1], cen_init[1], wid_init[1], gamma_init[1]

def estimate_double_gaussian_params(x, y):
    """
    Estimate good starting values for fitting a double Gaussian function.
    
    Parameters:
    - x: Array of x values.
    - y: Array of y values.
    
    Returns:
    - A1_init, mu1_init, sigma1_init: Estimated parameters for the first Gaussian.
    - A2_init, mu2_init, sigma2_init: Estimated parameters for the second Gaussian.
    """
    # Find two prominent peaks in the data
    peaks, _ = find_peaks(y, height=0.1, distance=len(x) // 5)  # Adjust parameters as necessary

    if len(peaks) < 2:
        raise ValueError("Less than two peaks found in the data. Ensure the data has two distinct peaks.")

    # Sort the peaks by height (prominence), highest peaks first
    sorted_peaks = peaks[np.argsort(y[peaks])][::-1]

    # Initialize arrays for the parameters
    amp_init = []
    cen_init = []
    sigma_init = []

    # Estimate parameters for each peak (top 2 peaks)
    for peak_idx in sorted_peaks[:2]:
        # Amplitude is the height at the peak
        A = y[peak_idx]
        
        # Center is the x-value at the peak
        mu = x[peak_idx]

        # Estimate FWHM by finding where the peak crosses half its maximum
        half_max = A / 2
        left_idx = np.where(y[:peak_idx] < half_max)[0][-1]  # Left crossing
        right_idx = np.where(y[peak_idx:] < half_max)[0][0] + peak_idx  # Right crossing

        fwhm = x[right_idx] - x[left_idx]
        
        # Estimate sigma from FWHM (Gaussian relationship: FWHM ≈ 2.355 * sigma)
        sigma = fwhm / 2.355

        # Append initial estimates
        amp_init.append(A)
        cen_init.append(mu)
        sigma_init.append(sigma)

    # Return initial parameters for both Gaussians
    A1_init, mu1_init, sigma1_init = amp_init[0], cen_init[0], sigma_init[0]
    A2_init, mu2_init, sigma2_init = amp_init[1], cen_init[1], sigma_init[1]
    
    return A1_init, mu1_init, sigma1_init, A2_init, mu2_init, sigma2_init

def estimate_double_lorentz_params(x, y):
    """
    Estimate good starting values for fitting a double Lorentzian function.
    
    Parameters:
    - x: Array of x values.
    - y: Array of y values.
    
    Returns:
    - A1_init, mu1_init, gamma1_init: Estimated parameters for the first Lorentzian.
    - A2_init, mu2_init, gamma2_init: Estimated parameters for the second Lorentzian.
    """
    # Find two prominent peaks in the data
    peaks, _ = find_peaks(y, height=0.1, distance=len(x) // 5)  # Adjust parameters if necessary

    if len(peaks) < 2:
        raise ValueError("Less than two peaks found in the data. Ensure the data has two distinct peaks.")

    # Sort peaks by height (prominence), highest peaks first
    sorted_peaks = peaks[np.argsort(y[peaks])][::-1]

    # Initialize arrays for the parameters
    amp_init = []
    cen_init = []
    gamma_init = []

    # Estimate parameters for each peak (top 2 peaks)
    for peak_idx in sorted_peaks[:2]:
        # Amplitude is the height at the peak
        A = y[peak_idx]
        
        # Center is the x-value at the peak
        mu = x[peak_idx]

        # Estimate HWHM by finding where the peak crosses half its maximum
        half_max = A / 2
        left_idx = np.where(y[:peak_idx] < half_max)[0][-1]  # Left crossing
        right_idx = np.where(y[peak_idx:] < half_max)[0][0] + peak_idx  # Right crossing

        fwhm = x[right_idx] - x[left_idx]
        
        # For Lorentzian, the HWHM is directly related to gamma
        gamma = fwhm / 2

        # Append initial estimates
        amp_init.append(A)
        cen_init.append(mu)
        gamma_init.append(gamma)

    # Return initial parameters for both Lorentzians
    A1_init, mu1_init, gamma1_init = amp_init[0], cen_init[0], gamma_init[0]
    A2_init, mu2_init, gamma2_init = amp_init[1], cen_init[1], gamma_init[1]
    
    return A1_init, mu1_init, gamma1_init, A2_init, mu2_init, gamma2_init

# fit window functions to data  
def fitdoublegaussiantospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    if guess is None:
        initialguess = estimate_double_gaussian_params(x, y)
    else:
        initialguess = guess[0:6]
    #[np.max(y), x[np.argmax(y)], np.std(x), np.max(y), x[np.argmax(y)], np.std(x)] #old fit estimate
    fitdata, pcov = curve_fit(double_gaussianwind, x, y, p0=initialguess, maxfev=maxfev)
    amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit, pcov

def fitdoublelorentztospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    if guess is None:
        initialguess = estimate_double_lorentz_params(x, y)
    else:
        initialguess = guess[0:6]
    #[np.max(y), x[np.argmax(y)], np.std(x), np.max(y), x[np.argmax(y)], np.std(x)] old fit estimate
    fitdata, pcov = curve_fit(double_lorentzwind, x, y, p0=initialguess, maxfev=maxfev)
    amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, amp2_fit, cen2_fit, wid2_fit, pcov

def fitdoublevoigttospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    if guess is None:
        initialguess = estimate_double_voigt_params(x, y)
    else:
        initialguess = guess[0:8]
    #[np.max(y), x[np.argmax(y)], np.std(x), np.std(x), np.max(y), x[np.argmax(y)], np.std(x), np.std(x)] old fit estimate
    fitdata, pcov = curve_fit(double_voigtwind, x, y, p0=initialguess, maxfev=maxfev,
                              # tighten fith convergence by setting bounds
                              ftol = 1e-10, xtol=1e-10, gtol=1e-10,
                              )
    amp1_fit, cen1_fit, wid1_fit, gamma1_fit, amp2_fit, cen2_fit, wid2_fit, gamma2_fit = fitdata
    return amp1_fit, cen1_fit, wid1_fit, gamma1_fit, amp2_fit, cen2_fit, wid2_fit, gamma2_fit, pcov

def fitvoigttospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    #initialguess = [np.max(y), x[np.argmax(y)], np.std(x)*2, np.std(x)]
    if guess is None:
        initialguess = estimate_voigt_params(x, y)
    else:
        initialguess = guess[0:4]
    fitdata, pcov = curve_fit(voigtwind, x, y, p0=initialguess, maxfev=maxfev)
    amp_fit, cen_fit, wid_fit, gamma_fit = fitdata
    return amp_fit, cen_fit, wid_fit, gamma_fit, pcov

def fitlorentztospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    if guess is None:
        initialguess = [np.max(y), x[np.argmax(y)], np.std(x)*2.4]
    else:
        initialguess = guess[0:3]
    fitdata, pcov = curve_fit(lorentzwind, x, y, p0=initialguess, maxfev=maxfev)
    amp_fit, cen_fit, wid_fit = fitdata
    return amp_fit, cen_fit, wid_fit, pcov

def fitgaussiantospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    if guess is None:
        initialguess = [np.max(y), x[np.argmax(y)], np.std(x)]
    else:
        initialguess = guess[0:3]
    #print('initialguess:', initialguess)
    #print('generated guess:', [np.max(y), x[np.argmax(y)], np.std(x)])
    fitdata, pcov = curve_fit(gaussianwind, x, y, p0=initialguess, maxfev=maxfev)
    amp_fit, cen_fit, wid_fit = fitdata
    return amp_fit, cen_fit, wid_fit, pcov
    
def fitlinetospec(start, end, WL, PLB, maxfev=10000, guess=None):
    x = WL[start: end]
    y = PLB[start: end]
    a_guess = (np.max(y) - np.min(y)) / (np.max(x) - np.min(x))
    b_guess = np.mean(y) - a_guess * np.mean(x)
    initial_guess = [a_guess, b_guess]
    fitdata, pconf = curve_fit(linearwind, x, y, p0=initial_guess, maxfev=maxfev)
    a, b = fitdata
    return a, b, pconf

# get maxima of fitted functions
def getmaxdoublegaussian(xmin, xmax, amp1, cen1, wid1, amp2, cen2, wid2):
    # use newton method to find max
    #x = Newtonmax(lambda x: -double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2), cen1, tol=1e-6, maxiter=10000, xmin=xmin, xmax=xmax)
    #y = double_gaussianwind(xmax, amp1, cen1, wid1, amp2, cen2, wid2)
    x, y = Maxbyinsert(lambda x: -double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2), [xmin, xmax], 10000)
    #success, x, fun = find_max_of_fit(lambda x: -double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2), xmin=xmin, xmax=xmax)
    return x, y # -fun

def getmaxdoublelorentz(xmin, xmax, amp1, cen1, wid1, amp2, cen2, wid2):
    #x = Newtonmax(lambda x: -double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2), cen1, tol=1e-6, maxiter=10000, xmin=xmin, xmax=xmax)
    #y = double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2)
    x, y = Maxbyinsert(lambda x: -double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2), [xmin, xmax], 10000)
    #success, x, fun = find_max_of_fit(lambda x: -double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2), xmin=xmin, xmax=xmax)
    return x, y #-fun

def getmaxdoublevoigt(xmin, xmax, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2):
    #x = Newtonmax(lambda x: -double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2), cen1, tol=1e-6, maxiter=10000, xmin=xmin, xmax=xmax)
    #y = double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2)
    x, y = Maxbyinsert(lambda x: -double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2), [xmin, xmax], 10000)
    #success, x, fun = find_max_of_fit(lambda x: -double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2), xmin=xmin, xmax=xmax)
    return x, y
    
# max of 1D Fit functions can be obtained by reading their parameters
def getmaxgaussian(xmin, xmax, amp, cen, wid):
    return cen, amp

def getmaxlorentz(xmin, xmax, amp, cen, wid):
    return cen, amp

def getmaxvoigt(xmin, xmax, amp, cen, wid, gamma):
    return cen, amp

def getmaxlinear(xmin, xmax, a, b):
    pass

# 2D Pixmatrix Fit functions
# 2d gaussian function
def gaussian2drot(coords, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    x, y = coords
    x, y = x - xo, y - yo
    a = (np.cos(theta)**2) / (2 * sigma_x**2) + (np.sin(theta)**2) / (2 * sigma_y**2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
    c = (np.sin(theta)**2) / (2 * sigma_x**2) + (np.cos(theta)**2) / (2 * sigma_y**2)
    g = amplitude * np.exp(-(a * x**2 + 2 * b * x * y + c * y**2)) + offset
    return g.ravel()

# 2d gaussian function
def gaussian2d(coords, amplitude, xo, yo, sigma_x, sigma_y, offset):
    x, y = coords
    x, y = x - xo, y - yo
    scale = amplitude / (2 * np.pi * sigma_x * sigma_y)
    g = scale * np.exp(-(x**2 / (2 * sigma_x**2) + y**2 / (2 * sigma_y**2))) + offset
    return g.ravel()

def fitgaussiand2dtomatrixrot(inpdata, plotfit, gdx, gdy, colormap, maxfev=10000):
    data = np.array(inpdata)
    x = np.arange(data.shape[1])
    y = np.arange(data.shape[0])
    x, y = np.meshgrid(x, y)
    initialguess = [np.max(data), np.argmax(data) % data.shape[1], np.argmax(data) // data.shape[1], 1, 1, 0, 0]
    popt, pcov = curve_fit(gaussian2drot, (x, y), data.ravel(), p0=initialguess, maxfev=maxfev)
    #fwhmx = 2 * np.sqrt(2 * np.log(2)) * fitdata[3]
    #fwhmy = 2 * np.sqrt(2 * np.log(2)) * fitdata[4]
    data_fited = gaussian2drot((x, y), *popt).reshape(data.shape)
    fwhmx = np.sqrt(2 * np.log(2)) * popt[3] * gdx * 2 
    fwhmy = np.sqrt(2 * np.log(2)) * popt[4] * gdy * 2 
    print('FWHM X = {} mum, FWHM Y = {} mum'.format(round(fwhmx, 2), round(fwhmy, 2)))
    # print when the fited function falls below 1/e of the maximum
    #beamx = np.where(data_fited > np.max(data_fited) / np.e)[1]*gdx
    #beamy = np.where(data_fited > np.max(data_fited) / np.e)[0]*gdx
    #print('Beam X = {} mum, Beam Y = {} mum'.format(np.amax(beamx)-np.amin(beamx), np.amax(beamy)-np.amin(beamy)))

    #calculate beam waist
    x0 = popt[1] * gdx
    sigma_x = popt[3] * gdx
    amplitude = popt[0]
    y0 = popt[2] * gdy
    sigma_y = popt[4] * gdy
    bwx_start = x0 - sigma_x*np.sqrt(2)
    bwx_end = x0 + sigma_x*np.sqrt(2)
    bwy_start = y0 - sigma_y*np.sqrt(2)
    bwy_end = y0 + sigma_y*np.sqrt(2)
    print('Beam Waist X = {} mum, Beam Waist Y = {} mum'.format(abs(bwx_end-bwx_start), abs(bwy_end-bwy_start)))

    # plot data_fited
    if plotfit == True:
        fig, ax = plt.subplots()
        plt.imshow(data_fited, cmap=colormap)

        # Get current ticks
        current_xticks = np.arange(data.shape[1])
        current_yticks = np.arange(data.shape[0])
        # Multiply ticks by constants
        new_xticks = np.multiply(current_xticks, gdx).round(3)
        new_yticks = np.multiply(current_yticks, gdy).round(3)
        # Set new ticks
        ax.set_xticks(current_xticks)  # Set the ticks to be at the indices of the current ticks
        ax.set_yticks(current_yticks)
        # Set tick labels to the new values
        ax.set_xticklabels(new_xticks)
        ax.set_yticklabels(new_yticks)
        # Set the axis labels auto adjust
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))  # Adjust the number of bins to fit the plot size
        # Set the title and labels
        ax.set_title('Fitted Gaussian 2D')
        ax.set_xlabel('X-axis in \u03bcm')
        ax.set_ylabel('Y-axis in \u03bcm')
        # label the colormap with the units counts
        cbar = plt.colorbar()
        cbar.set_label('Counts')

        plt.show()

def fitgaussian2dtomatrix(inpdata, plotfit, gdx, gdy, colormap, maxfev=10000):
    data = np.array(inpdata)
    x = np.arange(data.shape[1])
    y = np.arange(data.shape[0])
    x, y = np.meshgrid(x, y)
    initialguess = [np.max(data), np.argmax(data) % data.shape[1], np.argmax(data) // data.shape[1], 1, 1, 0]
    popt, pcov = curve_fit(gaussian2d, (x, y), data.ravel(), p0=initialguess, maxfev=maxfev)

    data_fited = gaussian2d((x, y), *popt).reshape(data.shape)
    fwhmx = np.sqrt(2 * np.log(2)) * popt[3] * gdx * 2 
    fwhmy = np.sqrt(2 * np.log(2)) * popt[4] * gdy * 2 
    print('FWHM X = {} mum, FWHM Y = {} mum'.format(round(fwhmx, 2), round(fwhmy, 2)))

    if plotfit == True:
        fig, ax = plt.subplots()  
        plt.imshow(data_fited, cmap=colormap)
        # Get current ticks
        current_xticks = np.arange(data.shape[1])
        current_yticks = np.arange(data.shape[0])
        # Multiply ticks by constants
        new_xticks = np.multiply(current_xticks, gdx).round(3)
        new_yticks = np.multiply(current_yticks, gdy).round(3)
        # Set new ticks
        ax.set_xticks(current_xticks)  # Set the ticks to be at the indices of the current ticks
        ax.set_yticks(current_yticks)
        # Set tick labels to the new values
        ax.set_xticklabels(new_xticks)
        ax.set_yticklabels(new_yticks)
        # Set the axis labels auto adjust
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))  # Adjust the number of bins to fit the plot size
        # Set the title and labels
        ax.set_title('Fitted Gaussian 2D')
        ax.set_xlabel('X-axis in \u03bcm')
        ax.set_ylabel('Y-axis in \u03bcm')
        # label the colormap with the units counts
        cbar = plt.colorbar()
        cbar.set_label('Counts')
        plt.show()

    #calculate beam waist
    x0 = popt[1] * gdx
    sigma_x = popt[3] * gdx
    amplitude = popt[0]
    y0 = popt[2] * gdy
    sigma_y = popt[4] * gdy
    bwx_start = x0 - sigma_x*np.sqrt(2)
    bwx_end = x0 + sigma_x*np.sqrt(2)
    bwy_start = y0 - sigma_y*np.sqrt(2)
    bwy_end = y0 + sigma_y*np.sqrt(2)
    print('Beam Waist X = {} mum, Beam Waist Y = {} mum'.format(abs(bwx_end-bwx_start), abs(bwy_end-bwy_start)))

# FWHM functions
def getlorentzfwhm(fitparams):
    # returns the FWHM of a lorentzian fit
    # fitparams: amp, cen, wid
    amp, cen, wid = fitparams[0:3]
    fwhm = 2 * wid
    return fwhm

def getgaussianfwhm(fitparams):
    # returns the FWHM of a gaussian fit
    # fitparams: amp, cen, wid
    amp, cen, wid = fitparams[0:3]
    fwhm = 2 * np.sqrt(2 * np.log(2)) * wid
    return fwhm

def getvoigtfwhm(fitparams):
    # returns the FWHM of a voigt fit
    # fitparams: amp, cen, wid, gamma
    amp, cen, wid, gamma = fitparams[0:4]
    # FWHM of a Voigt profile is not straightforward, so it is calculated on a grid using the fwhmbygrid function
    # 
    fwhm = fwhmbygrid(wid, cen - 5 * wid, cen + 5 * wid, npoints=10000)
    return fwhm

def getdoublegaussianfwhm(fitparams):
    # returns the FWHM of a double gaussian fit
    # fitparams: amp1, cen1, wid1, amp2, cen2, wid2
    amp1, cen1, wid1, amp2, cen2, wid2 = fitparams[0:6]
    fwhm1 = 2 * np.sqrt(2 * np.log(2)) * wid1
    fwhm2 = 2 * np.sqrt(2 * np.log(2)) * wid2
    return fwhm1 + fwhm2

def getdoublelorentzfwhm(fitparams):
    # returns the FWHM of a double lorentzian fit
    # fitparams: amp1, cen1, wid1, amp2, cen2, wid2
    amp1, cen1, wid1, amp2, cen2, wid2 = fitparams[0:6]
    fwhm1 = 2 * wid1
    fwhm2 = 2 * wid2
    return fwhm1 + fwhm2

def getdoublevoigtfwhm(fitparams):
    # returns the FWHM of a double voigt fit
    # fitparams: amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2
    amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2 = fitparams[0:8]
    # FWHM of a Voigt profile is not straightforward, so it is calculated on a grid using the fwhmbygrid function
    fwhm1 = fwhmbygrid(lambda x: voigtwind(x, amp1, cen1, wid1, gamma1), cen1 - 5 * wid1, cen1 + 5 * wid1)
    fwhm2 = fwhmbygrid(lambda x: voigtwind(x, amp2, cen2, wid2, gamma2), cen2 - 5 * wid2, cen2 + 5 * wid2)
    return fwhm1 + fwhm2

def fwhmbygrid(f, wlstart, wlend, npoints=100000):
    # Generate x values
    x = np.linspace(wlstart, wlend, npoints)
    # Calculate y values
    y = f(x)
    # Find the maximum y value
    ymax = np.max(y)
    # Find the half maximum value
    half_max = ymax / 2
    # Find where y crosses half_max
    left_idx = np.where(y > half_max)[0][0]  # First index where y > half max
    right_idx = np.where(y > half_max)[0][-1]  # Last index where y > half max
    # Calculate FWHM
    fwhm = x[right_idx] - x[left_idx]
    return fwhm

# newton's method to find the maximum of a function
def Newtonmax(f, x0, tol=1e-8, maxiter=10000, xmin=0, xmax=1000):
    # Initialize the iteration counter
    iter = 0
    # Initialize the error
    error = tol + 1
    # Iterate until the error is less than the tolerance or the maximum number of iterations is reached
    while error > tol and iter < maxiter and x0 > xmin and x0 < xmax:
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

def Maxbyinsert(f, wl, npoints):
    # Find the maximum of a function by inserting points
    # f: function to be maximized
    # wl: wavelength range
    # npoints: number of points to be inserted
    x = np.linspace(wl[0], wl[1], npoints)
    y = f(x)
    max_index = np.argmin(y)
    return x[max_index], y[max_index]

# another method to find the maximum of a function in an interval
def find_max_of_fit(fitfunc, tol=1e-6, maxiter=10000, xmin=500, xmax=600):
    #Find the maximum of a fitted function within the interval [xmin, xmax].
    notfound = True
    if xmax < xmin+10:
        xmax = xmin+100
    x0 = xmin
    while notfound == True: # if the maximum is not found, increase the initial guess
        result = minimize(lambda x: -fitfunc(x), x0=550, bounds=[(xmin, xmax)])
        if result.success:
            notfound = False
        else:
            if x0 > xmax:
                return False, x0, -fitfunc(x0)
            x0 += 10
    #print(result.x, -result.fun)
    #return result.success, result.x, -result.fun
    return result.success, result.x, fitfunc(result.x) # type: ignore   

# calculate the r_squared between fit and data
# r_squared = 1 - (ss_res / ss_tot) 
def calc_r_squared(fit, data): # args: data(observations), y_fit(model)
    # Note: lib9.py passes (observations, model) as (fit, data)
    # So 'fit' argument contains observations, 'data' argument contains model
    
    # Convert to numpy arrays to handle lists and ensure correct math
    obs = np.array(fit)
    model = np.array(data)
    
    # Calculate sums of squares
    # ss_res = sum((y_obs - y_model)^2)
    ss_res = np.sum((obs - model)**2)
    
    # ss_tot = sum((y_obs - mean(y_obs))^2)
    # We must calculate variance on OBSERVATIONS, not model
    ss_tot = np.sum((obs - np.mean(obs))**2)
    
    if ss_tot == 0:
        r_squared = 0.0
    else:
        r_squared = 1 - (ss_res / ss_tot)
        
    return r_squared, ss_res, ss_tot
# ss_res is the sum of the squared residuals
# ss_tot is the total sum of squares

# + is for ss_res, ss_tot, r_squared, pixstart, pixend, wlstart, wlend, fwhm, max_x, max_y
addtofitparms = ['ss_res', 'ss_tot', 'r_squared', 'fwhm', 'pixstart', 'pixend', 'wlstart', 'wlend', 'max_x', 'max_y', 'fit_status'] # Note: this one is essential to exist
unitstoaddfit = ['Counts', 'Counts', '', 'nm', 'nm', 'nm', 'nm', 'nm', 'nm', ''] # add further units to the array after r_squared
# add further parameters to the array after r_squared
def buildfitparas():
    fa = []
    for i in fitkeys.keys():
        fa.append([])#[np.nan])
        for j in range(0, fitkeys[i][4]+len(addtofitparms)):
            fa[-1].append(np.nan)
    return fa

# return a list of all fit parameters by their names
def getlistofallFitparameters():
    fl = []
    for i in fitkeys.keys():
        fl.append([])
        for j in range(0, fitkeys[i][4]):
            fl[-1].append(i + ' ' + str(j))
        for j in range(0, len(addtofitparms)):
            fl[-1].append(i + ' ' + addtofitparms[j])
    return fl

def getlistofallFitparaminone():
    fl = []
    for i in fitkeys.keys():
        for j in range(0, fitkeys[i][4]):
            fl.append(i + ' ' + str(j))
        for j in range(0, len(addtofitparms)):
            fl.append(i + ' ' + addtofitparms[j])
    return fl
    
def getindexofFitparameter(fl, fitname):# fl is a list of all fit parameters, returns the index of the fit parameter in the list
    for i in range(0, len(fl)):
        if fitname in fl[i]:
            return i, fl[i].index(fitname)
    return -1, -1

# obtain oscillations
# if a the signal is overlayed by a faster oscillation, the oscillation period is being isolated

def smooth_background(signal, window_length=51, polyorder=3):
    """
    Smooth the signal to extract the background using Savitzky-Golay filter.
    
    Parameters:
    - signal: Array of signal values
    - window_length: Length of the filter window (must be odd)
    - polyorder: Order of the polynomial used to fit the samples
    
    Returns:
    - Smoothed background signal
    """    
    # Ensure window_length is odd and less than signal length
    if window_length % 2 == 0:
        window_length += 1
    if window_length > len(signal):
        window_length = len(signal) if len(signal) % 2 == 1 else len(signal) - 1
    if window_length < polyorder + 2:
        window_length = polyorder + 2
        if window_length % 2 == 0:
            window_length += 1
    
    # Apply Savitzky-Golay filter for smoothing
    background = savgol_filter(signal, window_length, polyorder)
    return background

def extract_phase_evolution(oscillations, wl, maxima_indices, minima_indices):
    """
    Extract the phase evolution (instantaneous frequency) from oscillations.
    
    The phase changes as the oscillations speed up or slow down over the energy/wavelength range.
    
    Parameters:
    - oscillations: Array of isolated oscillations
    - wl: Wavelength/energy array
    - maxima_indices: Indices of maxima in oscillations
    - minima_indices: Indices of minima in oscillations
    
    Returns:
    - instantaneous_freq: Array of instantaneous frequency at each peak
    - freq_centers: Energy/wavelength values where frequency is calculated
    - phase_trend_slope: Linear fit slope of frequency evolution (chirp rate)
    - phase_trend_intercept: Linear fit intercept
    - mean_period: Mean oscillation period
    - period_std: Standard deviation of period (measure of chirp)
    """
    from scipy.signal import hilbert
    
    # Method 1: Calculate instantaneous frequency from peak spacing
    # Combine maxima and minima for better frequency estimation
    all_peaks = np.sort(np.concatenate([maxima_indices, minima_indices]))
    
    if len(all_peaks) < 3:
        # Not enough peaks to estimate phase evolution
        return (np.array([]), np.array([]), 0.0, 0.0, 0.0, 0.0)
    
    # Calculate period (spacing) between consecutive peaks
    peak_wl = wl[all_peaks]
    periods = np.diff(peak_wl)  # Period in energy/wavelength units
    
    # Instantaneous frequency is 1/period
    instantaneous_freq = 1.0 / periods
    freq_centers = (peak_wl[:-1] + peak_wl[1:]) / 2  # Midpoint between peaks
    
    # Fit linear trend to frequency evolution: freq(E) = slope * E + intercept
    # This captures the "chirp" or phase evolution
    if len(freq_centers) > 1:
        coeffs = np.polyfit(freq_centers, instantaneous_freq, 1)
        phase_trend_slope = coeffs[0]  # How fast frequency changes with energy
        phase_trend_intercept = coeffs[1]  # Initial frequency
    else:
        phase_trend_slope = 0.0
        phase_trend_intercept = instantaneous_freq[0] if len(instantaneous_freq) > 0 else 0.0
    
    # Calculate mean and std of period
    mean_period = np.mean(periods)
    period_std = np.std(periods)
    
    # Method 2: Use Hilbert transform for continuous phase (stored for potential future use)
    try:
        analytic_signal = hilbert(oscillations)
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))
        # Instantaneous frequency from phase derivative
        hilbert_freq = np.gradient(instantaneous_phase) / np.gradient(wl) / (2 * np.pi)
    except:
        hilbert_freq = None
    
    return (instantaneous_freq, freq_centers, phase_trend_slope, 
            phase_trend_intercept, mean_period, period_std)

def fitoscillationtospec(start, end, WL, PLB, maxfev=10000, guess=None):
    """
    Extract oscillations from spectrum and return fit parameters including phase evolution.
    
    Parameters:
    - start: Start index of the spectrum region
    - end: End index of the spectrum region
    - WL: Wavelength/energy array
    - PLB: Signal intensity array
    - maxfev: Not used, kept for compatibility
    - guess: Optional dict with 'window_length', 'polyorder', 'prominence', 'distance'
    
    Returns:
    - Tuple of fit parameters compatible with fitkeys structure:
      Scalar parameters (12 values):
        0: background_mean, 1: osc_amplitude, 2: n_maxima, 3: n_minima, 
        4: mean_max, 5: mean_min, 6: freq_est, 7: osc_range,
        8: phase_chirp (frequency evolution slope), 9: initial_freq (frequency at start),
        10: mean_period, 11: period_std (variability)
      Array parameters:
        background, oscillations, maxima_indices, minima_indices,
        maxima_wl, minima_wl, maxima_values, minima_values,
        instantaneous_freq, freq_centers
    """
    x = WL[start:end]
    y = PLB[start:end]
    
    # Parse optional parameters from guess
    window_length = 51
    polyorder = 3
    prominence = None
    distance = 5
    
    if guess is not None and isinstance(guess, dict):
        window_length = guess.get('window_length', 51)
        polyorder = guess.get('polyorder', 3)
        prominence = guess.get('prominence', None)
        distance = guess.get('distance', 5)
    
    # Call isolate_oscillation
    (background, oscillations, 
     maxima_indices, minima_indices,
     maxima_wl, minima_wl,
     maxima_values, minima_values) = isolate_oscillation(
        y, x, window_length, polyorder, prominence, distance
    )
    
    # Calculate summary statistics for fitkeys compatibility
    background_mean = np.mean(background)
    osc_amplitude = np.std(oscillations)
    n_maxima = len(maxima_indices)
    n_minima = len(minima_indices)
    mean_max = np.mean(maxima_values) if len(maxima_values) > 0 else 0
    mean_min = np.mean(minima_values) if len(minima_values) > 0 else 0
    
    # Estimate oscillation frequency (peaks per unit energy/wavelength)
    if n_maxima > 1:
        freq_est = n_maxima / (x[-1] - x[0])
    else:
        freq_est = 0
    
    osc_range = np.max(oscillations) - np.min(oscillations) if len(oscillations) > 0 else 0
    
    # Extract phase evolution (NEW!)
    (instantaneous_freq, freq_centers, phase_chirp, 
     initial_freq, mean_period, period_std) = extract_phase_evolution(
        oscillations, x, maxima_indices, minima_indices
    )
    
    # Return scalar parameters first (12 values for fitkeys compatibility), then arrays
    return (background_mean, osc_amplitude, n_maxima, n_minima, 
            mean_max, mean_min, freq_est, osc_range,
            phase_chirp, initial_freq, mean_period, period_std,  # NEW phase parameters
            background, oscillations, 
            maxima_indices, minima_indices,
            maxima_wl, minima_wl,
            maxima_values, minima_values,
            instantaneous_freq, freq_centers)  # NEW phase arrays

def getoscillationdata(xmin, xmax, *fitparams):
    """
    Extract oscillation data from fit parameters.
    This is a placeholder to maintain compatibility with fitkeys structure.
    
    Returns:
    - None (oscillation data is already in the fit parameters)
    """
    return None

def isolate_oscillation(signal, wl, window_length=51, polyorder=3, prominence=None, distance=5): 
    """
    Isolate oscillations from a signal that consists of a peak overlayed by faster oscillations.
    
    Parameters:
    - signal: Array of signal values (DR Signal)
    - wl: Array of wavelength/energy values corresponding to the signal
    - window_length: Length of the smoothing filter window (default: 51, must be odd)
    - polyorder: Order of polynomial for smoothing (default: 3)
    - prominence: Required prominence of peaks (default: auto-calculated)
    - distance: Minimum distance between peaks (default: 5)
    
    Returns:
    - background: Smoothed background signal
    - oscillations: Isolated oscillations (signal - background)
    - maxima_indices: Indices of maxima in the oscillations
    - minima_indices: Indices of minima in the oscillations
    - maxima_wl: Wavelength/energy values at maxima
    - minima_wl: Wavelength/energy values at minima
    - maxima_values: Signal values at maxima
    - minima_values: Signal values at minima
    """
    
    # Step 1: Smooth the signal to get the background
    background = smooth_background(signal, window_length, polyorder)
    
    # Step 2: Extract oscillations by subtracting background
    oscillations = signal - background
    
    # Step 3: Find maxima in the oscillations
    if prominence is None:
        # Auto-calculate prominence as a fraction of the oscillation range
        osc_range = np.max(oscillations) - np.min(oscillations)
        prominence = osc_range * 0.1  # 10% of the range
    
    maxima_indices, _ = find_peaks(oscillations, prominence=prominence, distance=distance)
    
    # Step 4: Find minima by inverting the oscillations
    minima_indices, _ = find_peaks(-oscillations, prominence=prominence, distance=distance)
    
    # Step 5: Extract wavelength and signal values at peaks
    maxima_wl = wl[maxima_indices] if len(maxima_indices) > 0 else np.array([])
    minima_wl = wl[minima_indices] if len(minima_indices) > 0 else np.array([])
    maxima_values = oscillations[maxima_indices] if len(maxima_indices) > 0 else np.array([])
    minima_values = oscillations[minima_indices] if len(minima_indices) > 0 else np.array([])
    
    return (background, oscillations, 
            maxima_indices, minima_indices,
            maxima_wl, minima_wl,
            maxima_values, minima_values)

    pass

# dictionary of window functions and their corresponding fit functions
# and functions to get the maxima of the fitted functions
# key: window function name
# value: list of window function, fit function, and function to get maxima of the fit function
# parnum: number of parameters for the fit function

'''
Note about the fit
fitparamunits array contains the following:

'''

# ============================================================================
# Stiffness Analysis Functions
# ============================================================================
# These functions analyze peak shape through flank slopes and top curvature
# without assuming specific line shapes (Voigt, Gaussian, etc.)

def find_baseline_region(intensity, noise_threshold=0.1):
    """
    Find baseline regions at start and end of spectrum.
    Returns indices where intensity is below noise_threshold * max(intensity).
    
    Parameters:
    -----------
    intensity : array
        Intensity values
    noise_threshold : float
        Fraction of max intensity to consider as baseline (default 0.1)
    
    Returns:
    --------
    left_base_idx : int
        Index of left baseline point
    right_base_idx : int
        Index of right baseline point
    """
    max_intensity = np.max(intensity)
    threshold = noise_threshold * max_intensity
    
    # Find left baseline (first point where intensity rises above threshold)
    left_base_idx = 0
    for i in range(len(intensity)):
        if intensity[i] > threshold:
            left_base_idx = max(0, i - 1)
            break
    
    # Find right baseline (last point where intensity drops below threshold)
    right_base_idx = len(intensity) - 1
    for i in range(len(intensity) - 1, -1, -1):
        if intensity[i] > threshold:
            right_base_idx = min(len(intensity) - 1, i + 1)
            break
    
    return left_base_idx, right_base_idx

def calculate_flank_slopes(energy, intensity, peak_fraction=0.5, smooth=False):
    """
    Calculate left and right flank slopes using linear regression.
    
    Parameters:
    -----------
    energy : array
        Energy values (x-axis)
    intensity : array
        Intensity values (y-axis)
    peak_fraction : float
        Fraction of peak height to use for flank definition (default 0.5 = 50%)
    smooth : bool
        Apply smoothing before calculation (default False)
    
    Returns:
    --------
    a_L : float
        Left flank slope (counts/eV)
    a_R : float
        Right flank slope (counts/eV)
    E_left_base : float
        Left baseline energy
    E_right_base : float
        Right baseline energy
    """
    # Smooth if requested
    if smooth and len(intensity) > 5:
        from scipy.ndimage import gaussian_filter1d
        intensity = gaussian_filter1d(intensity, sigma=1.0)
    
    # Find peak position
    peak_idx = np.argmax(intensity)
    peak_intensity = intensity[peak_idx]
    
    # Find baseline points
    left_base_idx, right_base_idx = find_baseline_region(intensity, noise_threshold=0.1)
    
    # Define flank regions (from baseline to peak_fraction of peak height)
    flank_threshold = peak_fraction * peak_intensity
    
    # Left flank: from left baseline to where intensity reaches flank_threshold
    left_flank_end = peak_idx
    for i in range(left_base_idx, peak_idx):
        if intensity[i] >= flank_threshold:
            left_flank_end = i
            break
    
    # Right flank: from peak to where intensity drops below flank_threshold
    right_flank_start = peak_idx
    for i in range(peak_idx, right_base_idx):
        if intensity[i] <= flank_threshold:
            right_flank_start = i
            break
    
    # Linear fit for left flank
    if left_flank_end > left_base_idx:
        x_left = energy[left_base_idx:left_flank_end+1]
        y_left = intensity[left_base_idx:left_flank_end+1]
        if len(x_left) > 1:
            poly_coeffs = np.polyfit(x_left, y_left, 1)
            a_L = float(poly_coeffs[0])
        else:
            a_L = 0.0
    else:
        a_L = 0.0
    
    # Linear fit for right flank
    if right_flank_start < right_base_idx:
        x_right = energy[right_flank_start:right_base_idx+1]
        y_right = intensity[right_flank_start:right_base_idx+1]
        if len(x_right) > 1:
            poly_coeffs = np.polyfit(x_right, y_right, 1)
            a_R = float(poly_coeffs[0])
        else:
            a_R = 0.0
    else:
        a_R = 0.0
    
    E_left_base = float(energy[left_base_idx])
    E_right_base = float(energy[right_base_idx])
    
    return a_L, a_R, E_left_base, E_right_base

def calculate_peak_curvature(energy, intensity, window_fraction=0.1):
    """
    Calculate peak-top curvature using quadratic fit.
    
    Parameters:
    -----------
    energy : array
        Energy values (x-axis)
    intensity : array
        Intensity values (y-axis)
    window_fraction : float
        Fraction of energy range to use for peak-top fit (default 0.1 = 10%)
    
    Returns:
    --------
    curvature : float
        Second derivative coefficient c_2 from quadratic fit (counts/eV²)
    E_max : float
        Energy at peak maximum
    I_max : float
        Intensity at peak maximum
    """
    # Find peak position
    peak_idx = np.argmax(intensity)
    E_max = float(energy[peak_idx])
    I_max = float(intensity[peak_idx])
    
    # Define window around peak
    energy_range = float(energy[-1] - energy[0])
    window_size = window_fraction * energy_range
    
    # Find indices within window
    window_mask = np.abs(energy - E_max) <= window_size / 2
    x_window = energy[window_mask]
    y_window = intensity[window_mask]
    
    # Quadratic fit: I(E) = c_0 + c_1*(E - E_max) + c_2*(E - E_max)²
    if len(x_window) >= 3:
        # Shift to center at E_max for better numerical stability
        x_shifted = x_window - E_max
        coeffs = np.polyfit(x_shifted, y_window, 2)
        curvature = float(coeffs[0])  # c_2 coefficient (second derivative / 2)
    else:
        curvature = 0.0
    
    return curvature, E_max, I_max

def calculate_asymmetry(a_L, a_R):
    """
    Calculate asymmetry metric from flank slopes.
    
    Parameters:
    -----------
    a_L : float
        Left flank slope (positive for rising edge)
    a_R : float
        Right flank slope (negative for falling edge)
    
    Returns:
    --------
    S_asym : float
        Asymmetry metric: (|a_R| - a_L) / (|a_R| + a_L)
        Range: -1 to +1
        0 = symmetric
        > 0 = steeper right side
        < 0 = steeper left side
    """
    abs_aR = float(np.abs(a_R))
    abs_aL = float(np.abs(a_L))
    denominator = abs_aR + abs_aL
    
    if denominator > 0:
        S_asym = float((abs_aR - abs_aL) / denominator)
    else:
        S_asym = 0.0
    
    return S_asym

def fitstiffnesstospec(start, end, WL, PLB, maxfev=10000, guess=None):
    """
    Perform stiffness analysis on spectrum.
    
    Parameters:
    -----------
    start : int
        Start index in arrays
    end : int
        End index in arrays
    WL : array
        Energy/wavelength array
    PLB : array
        Intensity array
    maxfev : int
        Not used (for compatibility with other fit functions)
    guess : array or None
        Not used (for compatibility with other fit functions)
    
    Returns:
    --------
    E_max : float
        Energy at peak maximum (eV)
    I_max : float
        Intensity at peak maximum (counts)
    a_L : float
        Left flank slope (counts/eV)
    a_R : float
        Right flank slope (counts/eV)
    S_asym : float
        Asymmetry metric (dimensionless)
    curvature : float
        Peak-top curvature (counts/eV²)
    pcov : None
        Placeholder for covariance matrix (not applicable here)
    """
    # Extract spectrum region - convert to numpy arrays explicitly
    x = np.array(WL[start:end])
    y = np.array(PLB[start:end])
    
    # Handle edge cases
    if len(x) < 3 or np.max(y) <= 0:
        # Return zeros if spectrum is too short or empty
        return float(0.0), float(0.0), float(0.0), float(0.0), float(0.0), float(0.0), None
    
    # Find peak position first
    peak_idx = np.argmax(y)
    E_max = float(x[peak_idx])
    I_max = float(y[peak_idx])
    
    # Calculate flank slopes
    try:
        a_L, a_R, _, _ = calculate_flank_slopes(x, y, peak_fraction=0.5, smooth=False)
        a_L = float(a_L)
        a_R = float(a_R)
    except:
        a_L = float(0.0)
        a_R = float(0.0)
    
    # Calculate peak curvature
    try:
        curvature, _, _ = calculate_peak_curvature(x, y, window_fraction=0.1)
        curvature = float(curvature)
    except:
        curvature = float(0.0)
    
    # Calculate asymmetry
    try:
        S_asym = calculate_asymmetry(a_L, a_R)
        S_asym = float(S_asym)
    except:
        S_asym = float(0.0)
    
    return E_max, I_max, a_L, a_R, S_asym, curvature, None

def stiffness_window(x, E_max, I_max, a_L, a_R, S_asym, curvature):
    """
    Construct a split Gaussian peak from stiffness parameters for visualization.
    Widths are estimated from flank slopes to provide a visual check of the analysis.
    """
    # Ensure x is a numpy array for element-wise operations
    x = np.array(x)
    
    # Factor relating max slope to width for Gaussian: max_slope = I_max / (sigma * sqrt(e))
    # sigma = I_max / (max_slope * sqrt(e))
    # sqrt(e) approx 1.6487
    factor = 1.6487
    
    # Estimate widths from slopes (handle potential zeros)
    if abs(a_L) > 1e-9:
        sigma_L = I_max / (abs(a_L) * factor)
    else:
        sigma_L = 1.0 # Fallback
        
    if abs(a_R) > 1e-9:
        sigma_R = I_max / (abs(a_R) * factor)
    else:
        sigma_R = 1.0 # Fallback
    
    # Construct split Gaussian
    y = np.zeros_like(x)
    
    # Left side (x < E_max)
    mask_L = x < E_max
    if np.any(mask_L):
        y[mask_L] = I_max * np.exp(-(x[mask_L] - E_max)**2 / (2 * sigma_L**2))
    
    # Right side (x >= E_max)
    mask_R = x >= E_max
    if np.any(mask_R):
        y[mask_R] = I_max * np.exp(-(x[mask_R] - E_max)**2 / (2 * sigma_R**2))
        
    return y

def getstiffnessfwhm(params):
    """
    Estimate FWHM from stiffness parameters (using split Gaussian approximation).
    params: [E_max, I_max, a_L, a_R, S_asym, curvature]
    """
    try:
        I_max = params[1]
        a_L = params[2]
        a_R = params[3]
        
        factor = 1.6487 # sqrt(e)
        
        if abs(a_L) > 1e-9:
            sigma_L = I_max / (abs(a_L) * factor)
        else:
            sigma_L = 0.0
            
        if abs(a_R) > 1e-9:
            sigma_R = I_max / (abs(a_R) * factor)
        else:
            sigma_R = 0.0
            
        # FWHM approx 2.355 * sigma (average sigma)
        fwhm = 2.355 * (sigma_L + sigma_R) / 2
        return fwhm
    except:
        return 0.0

def getmaxstiffness(xmin, xmax, E_max, I_max, a_L, a_R, S_asym, curvature):
    """
    Get maximum position from stiffness analysis parameters.
    
    Parameters:
    -----------
    xmin, xmax : float
        Energy range (not used, for compatibility)
    E_max : float
        Energy at peak maximum
    I_max : float
        Intensity at peak maximum
    a_L, a_R, S_asym, curvature : float
        Other stiffness parameters (not used here)
    
    Returns:
    --------
    E_max : float
        Energy at peak maximum
    I_max : float
        Intensity at peak maximum
    """
    return E_max, I_max

# ============================================================================
# Derivative Analysis Functions (Savitzky-Golay)
# ============================================================================

def fitderivativestospec(start, end, WL, PLB, maxfev=10000, guess=None):
    """
    Perform derivative-based analysis using Savitzky-Golay filter.
    Calculates max slope (1st derivative) and peak curvature (2nd derivative).
    
    Parameters:
    -----------
    start, end, WL, PLB, maxfev, guess: Standard fit function parameters
    
    Returns:
    --------
    E_max : float
        Energy at peak maximum
    I_max : float
        Intensity at peak maximum
    Max_Slope_Rise : float
        Maximum positive slope (rising edge)
    Max_Slope_Fall : float
        Maximum negative slope (falling edge)
    Curvature_Top : float
        Second derivative at peak maximum (curvature)
    S_asym_deriv : float
        Asymmetry based on max slopes: (|Fall| - Rise) / (|Fall| + Rise)
    pcov : None
    """
    # Extract spectrum region
    x = np.array(WL[start:end])
    y = np.array(PLB[start:end])
    
    # Handle edge cases
    if len(x) < 5 or np.max(y) <= 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None
        
    # Parameters for Savitzky-Golay
    # Window length must be odd and <= len(x)
    window_length = min(11, len(x))
    if window_length % 2 == 0:
        window_length -= 1
    if window_length < 5:
        window_length = len(x) if len(x) % 2 != 0 else len(x) - 1
        
    polyorder = 3
    
    try:
        # Calculate derivatives
        # delta x is needed for correct scaling of derivatives
        dx = np.mean(np.diff(x))
        
        # 0th derivative (smoothed intensity)
        y_smooth = savgol_filter(y, window_length, polyorder, deriv=0)
        
        # 1st derivative (slope)
        d1 = savgol_filter(y, window_length, polyorder, deriv=1, delta=dx)
        
        # 2nd derivative (curvature)
        d2 = savgol_filter(y, window_length, polyorder, deriv=2, delta=dx)
        
        # Find peak position from smoothed data
        peak_idx = np.argmax(y_smooth)
        E_max = float(x[peak_idx])
        I_max = float(y_smooth[peak_idx])
        
        # Max slope on rising edge (before peak)
        if peak_idx > 0:
            max_slope_rise = float(np.max(d1[:peak_idx]))
        else:
            max_slope_rise = 0.0
            
        # Max slope on falling edge (after peak) - should be negative
        if peak_idx < len(d1) - 1:
            max_slope_fall = float(np.min(d1[peak_idx:]))
        else:
            max_slope_fall = 0.0
            
        # Curvature at peak (2nd derivative at peak index)
        curvature_top = float(d2[peak_idx])
        
        # Asymmetry metric based on max slopes
        abs_fall = abs(max_slope_fall)
        abs_rise = abs(max_slope_rise)
        denom = abs_fall + abs_rise
        
        if denom > 0:
            s_asym = float((abs_fall - abs_rise) / denom)
        else:
            s_asym = 0.0
            
        return E_max, I_max, max_slope_rise, max_slope_fall, curvature_top, s_asym, None
        
    except Exception as e:
        print(f"Derivative analysis failed: {e}")
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None

def derivative_window(x, E_max, I_max, slope_rise, slope_fall, curvature, s_asym):
    """
    Construct a visualization for derivative analysis.
    Uses a split Gaussian approximated from the max slopes.
    """
    x = np.array(x)
    
    # Approximation: For Gaussian, max slope occurs at sigma.
    # Max slope value = I_max * exp(-0.5) / sigma
    # So sigma = I_max * exp(-0.5) / max_slope
    # exp(-0.5) approx 0.6065
    factor = 0.6065
    
    if abs(slope_rise) > 1e-9:
        sigma_L = (I_max * factor) / abs(slope_rise)
    else:
        sigma_L = 1.0
        
    if abs(slope_fall) > 1e-9:
        sigma_R = (I_max * factor) / abs(slope_fall)
    else:
        sigma_R = 1.0
        
    y = np.zeros_like(x)
    
    # Left side
    mask_L = x < E_max
    if np.any(mask_L):
        y[mask_L] = I_max * np.exp(-(x[mask_L] - E_max)**2 / (2 * sigma_L**2))
        
    # Right side
    mask_R = x >= E_max
    if np.any(mask_R):
        y[mask_R] = I_max * np.exp(-(x[mask_R] - E_max)**2 / (2 * sigma_R**2))
        
    return y

def getderivativefwhm(params):
    """
    Estimate FWHM from derivative parameters.
    params: [E_max, I_max, slope_rise, slope_fall, curvature, s_asym]
    """
    try:
        I_max = params[1]
        slope_rise = params[2]
        slope_fall = params[3]
        
        factor = 0.6065 # exp(-0.5)
        
        if abs(slope_rise) > 1e-9:
            sigma_L = (I_max * factor) / abs(slope_rise)
        else:
            sigma_L = 0.0
            
        if abs(slope_fall) > 1e-9:
            sigma_R = (I_max * factor) / abs(slope_fall)
        else:
            sigma_R = 0.0
            
        return 2.355 * (sigma_L + sigma_R) / 2
    except:
        return 0.0

def getmaxderivative(xmin, xmax, E_max, I_max, *args):
    return E_max, I_max

# ============================================================================
# End of Stiffness Analysis Functions
# ============================================================================

fitkeys = {'lorentz':[lorentzwind, fitlorentztospec, getmaxlorentz, 'Lorentz fit', 3, ['Lorentzian amplitude', 'Lorentzian center', 'Lorentzian width'], ['Counts', 'nm', 'nm'], getlorentzfwhm, 0],
           'gaussian':[gaussianwind, fitgaussiantospec, getmaxgaussian, 'Gaussian fit', 3, ['Gaussian amplitude', 'Gaussian center', 'Gaussian width'], ['Counts', 'nm', 'nm'], getgaussianfwhm, 0],
           'voigt':[voigtwind, fitvoigttospec, getmaxvoigt, 'Voigt fit', 4, ['Voigt amplitude', 'Voigt center', 'Voigt width', 'Voigt gamma'], ['Counts', 'nm', 'nm', 'nm'], getvoigtfwhm, 0], 
           'linear':[linearwind, fitlinetospec, getmaxlinear, 'Linear fit', 2, ['Linear slope', 'Linear offset'], ['nm', 'Counts'], None, 0],
           'double lorentz':[double_lorentzwind, fitdoublelorentztospec, getmaxdoublelorentz, 'Double Lorentz fit', 6, ['Double Lorentzian amplitude 1', 'Double Lorentzian center 1', 'Double Lorentzian width 1', 'Double Lorentzian amplitude 2', 'Double Lorentzian center 2', 'Double Lorentzian width 2'], ['Counts', 'nm', 'nm', 'Counts', 'nm', 'nm'], getdoublelorentzfwhm, 0], 
           'double gaussian':[double_gaussianwind, fitdoublegaussiantospec, getmaxdoublegaussian, 'Double Gaussian fit', 6, ['Double Gaussian amplitude 1', 'Double Gaussian center 1', 'Double Gaussian width 1', 'Double Gaussian amplitude 2', 'Double Gaussian center 2', 'Double Gaussian width 2'], ['Counts', 'nm', 'nm', 'Counts', 'nm', 'nm'], getdoublegaussianfwhm, 0], 
           'double voigt':[
               double_voigtwind, fitdoublevoigttospec, getmaxdoublevoigt, 'Double Voigt fit', 8, ['Double Voigt amplitude 1', 'Double Voigt center 1', 'Double Voigt width 1', 'Double Voigt gamma 1', 'Double Voigt amplitude 2', 'Double Voigt center 2', 'Double Voigt width 2', 'Double Voigt gamma 2'], ['Counts', 'nm', 'nm', 'nm', 'Counts', 'nm', 'nm', 'nm'], getdoublevoigtfwhm, 0
               ],
           'oscillations': [
               None,  # No window function for oscillations (uses isolate_oscillation internally)
               fitoscillationtospec,  # Fitting function
               getoscillationdata,  # Placeholder for compatibility
               'Oscillation Extraction with Phase', 
               12,  # Number of scalar output parameters (including phase evolution)
               ['Background mean', 'Oscillation amplitude', 'Number of maxima', 'Number of minima', 
                'Mean maxima value', 'Mean minima value', 'Oscillation frequency estimate', 'Oscillation range',
                'Phase chirp rate', 'Initial frequency', 'Mean period', 'Period std dev'],
               ['Counts', 'Counts', '', '', 'Counts', 'Counts', 'eV^-1', 'Counts',
                'eV^-2', 'eV^-1', 'eV', 'eV'],
               None, # No FWHM function
               0 # fit state: 0= not fitted, 1=fitted, 2=failed
           ],
           'stiffness': [
               stiffness_window,  # Window function (returns zeros)
               fitstiffnesstospec,  # Analysis function
               getmaxstiffness,  # Get peak position
               'Stiffness Analysis',  # Label for GUI
               6,  # Number of output parameters
               ['Peak Energy', 'Peak Intensity', 'Left Stiffness', 'Right Stiffness', 'Asymmetry', 'Curvature'],
               ['eV', 'Counts', 'Counts/eV', 'Counts/eV', '', 'Counts/eV²'],
               getstiffnessfwhm,  # FWHM function (returns 0.0)
               0  # fit state: 0= not fitted, 1=fitted, 2=failed
           ],
           'derivative': [
               derivative_window,
               fitderivativestospec,
               getmaxderivative,
               'Derivative Analysis (SG)',
               6,
               ['Peak Energy', 'Peak Intensity', 'Max Rise Slope', 'Max Fall Slope', 'Peak Curvature', 'Slope Asymmetry'],
               ['eV', 'Counts', 'Counts/eV', 'Counts/eV', 'Counts/eV²', ''],
               getderivativefwhm,
               0
           ]
           }


fitunits = {'lorentz': fitkeys['lorentz'][6][:]+ unitstoaddfit,
            'gaussian': fitkeys['gaussian'][6][:] + unitstoaddfit,
            'voigt': fitkeys['voigt'][6][:] + unitstoaddfit,
            'linear': fitkeys['linear'][6][:] + unitstoaddfit,
            'double lorentz': fitkeys['double lorentz'][6][:] + unitstoaddfit,
            'double gaussian': fitkeys['double gaussian'][6][:] + unitstoaddfit,
            'double voigt': fitkeys['double voigt'][6][:] + unitstoaddfit, 
            'oscillations': fitkeys['oscillations'][6][:]+ unitstoaddfit,
            'stiffness': fitkeys['stiffness'][6][:] + unitstoaddfit,
            'derivative': fitkeys['derivative'][6][:] + unitstoaddfit
            }

# fitparametersparis: dict of the fit parameters and their units. Key of getlistofallFitparameters() is the key of the fitkeys dictionary
# fitunitparis: dict of the fit parameters and their units. Key of getlist
fitunitparis = {}
all_fit_params = getlistofallFitparameters()
for i in range(len(all_fit_params)):
    fit_type = list(fitkeys.keys())[i]
    #print(i, fit_type, all_fit_params[i])
    #for j, param_name in enumerate(all_fit_params[i]):
    #    if j < fitkeys[fit_type][4]:  # Regular fit parameters
    #        fitunitparis[param_name] = fitunits[fit_type][j]
    #    else:  # Additional parameters (ss_res, ss_tot, etc.)
    #        fitunitparis[param_name] = fitunits[fit_type][j]

if __name__ == '__main__':
    print('This is a library of window functions and their corresponding fit functions.')
    print('Use the fitkeys dictionary to access the functions.')

    ''' print fit units:'''
    print('Fit units:')
    for key in fitunits.keys():
        print(f"{key}: {fitunits[key]}")

    print('Fit unit paris:')
    for key in fitunitparis.keys():
        print(f"{key}: {fitunitparis[key]}")
    
    ''' print fit parameters:
    print('Fit parameters:')
    for key in fitkeys.keys():
        print(f"{key}: {fitkeys[key][5]}")

    #print fit keys:
    print('Fit keys:')
    for key in fitkeys.keys():
        print(key)
    '''

    #print fit parameters:
    #print(getlistofallFitparameters())
    #print(len(getlistofallFitparameters()))
    