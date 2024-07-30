import numpy as np
from scipy.optimize import curve_fit, minimize
from scipy.special import wofz
from scipy.optimize import fminbound
from scipy.special import jv
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
def getmaxdoublegaussian(xmin, xmax, amp1, cen1, wid1, amp2, cen2, wid2):
    # use newton method to find max
    #xmax = Newtonmax(lambda x: -double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2), cen1, tol=1e-6, maxiter=10000, xmin=xmin, xmax=xmax)
    #ymax = double_gaussianwind(xmax, amp1, cen1, wid1, amp2, cen2, wid2)
    success, x, fun = find_max_of_fit(lambda x: -double_gaussianwind(x, amp1, cen1, wid1, amp2, cen2, wid2), xmin=xmin, xmax=xmax)
    return x, -fun


def getmaxdoublelorentz(xmin, xmax, amp1, cen1, wid1, amp2, cen2, wid2):
    #xmax = Newtonmax(lambda x: -double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2), cen1, tol=1e-6, maxiter=10000, xmin=xmin, xmax=xmax)
    #ymax = double_lorentzwind(xmax, amp1, cen1, wid1, amp2, cen2, wid2)
    success, x, fun = find_max_of_fit(lambda x: -double_lorentzwind(x, amp1, cen1, wid1, amp2, cen2, wid2), xmin=xmin, xmax=xmax)
    return x, -fun

def getmaxdoublevoigt(xmin, xmax, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2):
    xmax = Newtonmax(lambda x: -double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2), cen1, tol=1e-6, maxiter=10000, xmin=xmin, xmax=xmax)
    ymax = double_voigtwind(xmax, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2)
    #success, x, fun = find_max_of_fit(lambda x: -double_voigtwind(x, amp1, cen1, wid1, gamma1, amp2, cen2, wid2, gamma2), xmin=xmin, xmax=xmax)
    #return x, -fun
    return xmax, ymax

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

# 2d bessel function
def bessel2d(xy, A, B, x0, y0):
    x, y = xy
    r = np.sqrt((x - x0)**2 + (y - y0)**2)
    return A * jv(0, B*r) 

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
        plt.colorbar()

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

# newton's method to find the maximum of a function
def Newtonmax(f, x0, tol=1e-6, maxiter=10000, xmin=0, xmax=1000):
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

# another method to find the maximum of a function in an interval
def find_max_of_fit(fitfunc, tol=1e-6, maxiter=10000, xmin=0, xmax=1000):
    #Find the maximum of a fitted function within the interval [xmin, xmax].
    result = minimize(lambda x: -fitfunc(x), x0=550, bounds=[(xmin, xmax)])
    print(result.x, -result.fun)
    return result.success, result.x, -result.fun

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

