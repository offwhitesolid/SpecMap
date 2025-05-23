import numpy as np
import os, sys
from scipy.optimize import curve_fit
from scipy.special import jv
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# 2D Pixmatrix Fit functions
# 2d gaussian function
def gaussian2d(coords, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    x, y = coords
    x, y = x - xo, y - yo
    a = (np.cos(theta)**2) / (2 * sigma_x**2) + (np.sin(theta)**2) / (2 * sigma_y**2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x**2) + (np.sin(2 * theta)) / (4 * sigma_y**2)
    c = (np.sin(theta)**2) / (2 * sigma_x**2) + (np.cos(theta)**2) / (2 * sigma_y**2)
    g = amplitude * np.exp(-(a * x**2 + 2 * b * x * y + c * y**2)) + offset
    return g.ravel()

def fitgaussiand2dtomatrix(inpdata, plotfit, gdx, gdy, colormap, pos, savedir, maxfev=10000):
    data = np.array(inpdata)
    x = np.arange(data.shape[1])
    y = np.arange(data.shape[0])
    x, y = np.meshgrid(x, y)
    initialguess = [np.max(data), np.argmax(data) % data.shape[1], np.argmax(data) // data.shape[1], 1, 1, 0, 0]
    popt, pcov = curve_fit(gaussian2d, (x, y), data.ravel(), p0=initialguess, maxfev=maxfev)
    #fwhmx = 2 * np.sqrt(2 * np.log(2)) * fitdata[3]
    #fwhmy = 2 * np.sqrt(2 * np.log(2)) * fitdata[4]
    data_fited = gaussian2d((x, y), *popt).reshape(data.shape)
    fwhmx = np.sqrt(2 * np.log(2)) * popt[3] * gdx * 2 
    fwhmy = np.sqrt(2 * np.log(2)) * popt[4] * gdy * 2 
    print('FWHM X = {} mum, FWHM Y = {} mum'.format(round(fwhmx, 2), round(fwhmy, 2)))
    # print when the fited function falls below 1/e of the maximum
    #beamx = np.where(data_fited > np.max(data_fited) / np.e)[1]*gdx
    #beamy = np.where(data_fited > np.max(data_fited) / np.e)[0]*gdx
    #print('Beam X = {} mum, Beam Y = {} mum'.format(np.amax(beamx)-np.amin(beamx), np.amax(beamy)-np.amin(beamy)))
    # plot data_fited
    if plotfit == True:
        fig, ax = plt.subplots()
        plt.imshow(data_fited, cmap=colormap)
        plt.colorbar()

        # Get current ticks
        current_xticks = np.arange(data.shape[1])
        current_yticks = np.arange(data.shape[0])

        # Multiply ticks by constants
        new_xticks = np.multiply(current_xticks, gdx).round(5)
        new_yticks = np.multiply(current_yticks, gdy).round(5)

        # Set new ticks
        ax.set_xticks(current_xticks)  # Set the ticks to be at the indices of the current ticks
        ax.set_yticks(current_yticks)

        # Set tick labels to the new values
        ax.set_xticklabels(new_xticks)
        ax.set_yticklabels(new_yticks)

        # Set the axis labels auto adjust
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))  # Adjust the number of bins to fit the plot size

        #plt.show()
        plt.savefig('{}/{}_fit.png'.format(savedir, pos))
        plt.show()
        plt.close()
        sys.exit()

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
    print('Beam Waist X = {} mum, Beam Waist Y = {} mum'.format(bwx_end-bwx_start, bwy_end-bwy_start))
    # write beam waist to file
    with open('waist.txt', 'a') as f:
        f.write('{}\t{}\t{}\n'.format(float(pos.replace('_', '.')), bwx_end-bwx_start, bwy_end-bwy_start))

def fit2dgausstopixmatrix(data, gdx, gdy, pos=0):
    try:
        fitgaussiand2dtomatrix(data, True, gdx, gdy, 'viridis', pos, maxfev=10000)
        #fitdata, pcov, fwhmx, fwhmy = matl.fitgaussiand2dtomatrix(self.PixMatrix, maxfev=self.maxiter)
        #print(fitdata, pcov, fwhmx, fwhmy)

    except Exception as Error:
        print(Error)

filedir = 'C:\\Users\\mol95ww\\Desktop\\Evaluation\\data\\2024\\qdot_100fach\\Laser_in_zpos'
fend = '.asc'
savedir = 'C:\\Users\\mol95ww\\Desktop\\Promotion\\Reports\\2024\\240723\\images'

gdx = 0.0556
gdy = 0.0556

with open('waist.txt', 'w') as f:
    f.write('z-pos [mum]\tbwx[mum]\tbwy[mum]\n')

def getfiles(filedir, end='.asc'):
    files = []
    for file in os.listdir(filedir):
        if file.endswith(end):
            files.append(file)
    return files

files = getfiles(filedir, fend)

for file in files:
    with open(''.join([filedir, '\\', file])) as f:
        for i in range(34):
            f.readline()
        fload = f.readlines()
    x = []
    y = []
    data = []
    for i in fload:
        isplit = i.split('\n')[0].split('\t')
        x.append(float(isplit[0]))
        for j in range(1, len(isplit)):
            if isplit[j] == '':
                pass
            else:
                y.append(float(isplit[j]))
        data.append(y)
        y = []

    # plot the image
    plt.imshow(data, cmap='viridis')
    plt.colorbar()
    plt.show()
    plt.savefig('{}/{}.png'.format(savedir, file.split('.')[0]))
    plt.close()
    fit2dgausstopixmatrix(data, gdx, gdy, pos=file.split('.')[0])