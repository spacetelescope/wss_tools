''' Module to recenter images '''
import os
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

__all__ = ['rebin', 'recenter']


def rebin(arr, new_shape):
    ''' rebin(arr, new_shape)
    Parameters
    ----------
    arr: 2D array
    new_shape: dimensions of new shape
    Returns
    ----------
    newarr - Rebin 2D array arr to shape new_shape by averaging
    '''
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    newarr = np.nanmedian(np.nanmedian(arr.reshape(shape), axis=-1), axis=1)

    return newarr


def recenter(images, outputdir, doplot=False):
    ''' recenter(images, outputdir, doplot=False)
   Parameters
   ----------
   images:
   outputdir: dimensions of new shape
   doplot: boolean
   Returns
   ----------
   newarr - Rebin 2D array arr to shape new_shape by averaging
   '''
    output_images = []
    for im_fn in images:
        # Open fits
        hdul = fits.open(im_fn)
        data = hdul[1].data

        # Rebin image with very big pixels to find the approximate location
        size = 32
        rebindata = rebin(data, [size, size])

        # Remove background
        rebindata -= np.median(rebindata)

        margin_left = 1.5
        margin_right = 2.5
        margin_top = 2.5
        margin_bottom = 1.5
        imsize = 2048

        # Find the center of mass and cut a box around: we should see the whole
        # PSF with about 1-2 PSF wide margins
        com = ndimage.center_of_mass(rebindata)
        subdata = data[int((com[0] - margin_left) * imsize / size):
                       int((com[0] + margin_right) * imsize / size),
                       int((com[1] - margin_bottom) * imsize / size):
                       int((com[1] + margin_top) * imsize / size)]

        # Rebin again
        rebinsubdata = rebin(subdata, [size, size])

        # Remove background
        rebinsubdata -= np.median(rebinsubdata)

        # Find the center of mass and cut a box around: should see the inside
        # of the PSF
        com1 = ndimage.center_of_mass(rebinsubdata)
        margin_left2 = 0.5
        margin_right2 = 1.5
        margin_bottom2 = 0.5
        margin_top2 = 1.5
        subdata2 = \
            subdata[int((com1[0] - margin_left2) * imsize / size * 4 / size):
                    int((com1[0] + margin_right2) * imsize / size * 4 / size),
                    int((com1[1] - margin_bottom2) * imsize / size * 4 / size):
                    int((com1[1] + margin_top2) * imsize / size * 4 / size)]

        # Find the center of mass
        com2 = ndimage.center_of_mass(subdata2)

        xcntr = 464
        ycntr = 1412

        # Recenter the image to 464, 1412 instead to match the WAS expectations
        xcpsf = com2[0] + int((com1[0] - margin_left2)
                              * imsize / size * 4 / size)\
                        + int((com[0] - margin_left) * imsize / size)
        ycpsf = com2[1] + int((com1[1] - margin_bottom2)
                              * imsize / size * 4 / size) \
                        + int((com[1] - margin_bottom) * imsize / size)
        offsetdata = np.roll(data, (xcntr - int(ycpsf),
                                    ycntr - int(xcpsf)),
                             axis=(1, 0))

        # Save back image into file
        if abs(xcntr - ycpsf) > 10 or abs(ycntr - xcpsf) > 10:
            # Do the same for the ERR and the DQ
            hdul[2].data = np.roll(hdul[2].data,
                                   (xcntr - int(ycpsf), ycntr - int(xcpsf)),
                                   axis=(1, 0))
            hdul[3].data = np.roll(hdul[3].data,
                                   (xcntr - int(ycpsf), ycntr - int(xcpsf)),
                                   axis=(1, 0))
            hdul[1].data = offsetdata
            filename = os.path.basename(im_fn).replace('.fits',
                                                       '_recenter.fits')
            hdul.writeto(os.path.join(outputdir, filename), overwrite=True)
            output_images.append(os.path.join(outputdir, filename))
        else:
            output_images.append(im_fn)

        # Plot

        fig, ((ax1, ax2),
              (ax3, ax4),
              (ax5, ax6)) = plt.subplots(3, 2, figsize=(12, 9))
        fig.tight_layout(pad=.3)
        ax1.imshow(data, origin='lower')
        ax2.imshow(rebindata, origin='lower')

        ax3.imshow(subdata, origin='lower')
        ax4.imshow(rebinsubdata, origin='lower')

        ax5.imshow(subdata2, origin='lower')
        ax5.plot([com2[1], com2[1]], [0, imsize/size*4/size*2-1], 'r')
        ax5.plot([0, imsize/size*4/size*2-1], [com2[0], com2[0]], 'r')

        ax6.imshow(offsetdata, origin='lower')
        ax6.plot([xcntr, xcntr], [0, imsize-1], 'r')
        ax6.plot([0, imsize-1], [ycntr, ycntr], 'r')
        if doplot:
            plt.show()
        else:
            plt.savefig(os.path.join(outputdir, 'plot.png'))
    return output_images
