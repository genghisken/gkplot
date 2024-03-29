#!/usr/bin/env python
"""Plot an ATLAS detector heatmap from an input file - or import the plotHeatMap function. Input file needs headed rows called x and y.

Usage:
  %s <filename> [--outputFile=<file>] [--title=<title>] [--heatmapresolution=<heatmapresolution>] [--delimiter=<delimiter>] [--multiplier=<multiplier>] [--grid] [--colorbar] [--mask] [--horizontal] [--matrixfile]
  %s (-h | --help)
  %s --version

Options:
  -h --help                                 Show this screen.
  --version                                 Show version.
  --outputFile=<file>                       Output file. If not defined, show plot.
  --title=<title>                           Plot title.
  --heatmapresolution=<heatmapresolution>   Heatmap resolution as a power of 2 between 8 and 512 [default: 128].
  --delimiter=<delimiter>                   Delimiter to use [default: \\t].
  --multiplier=<multiplier>                 Multiplier for the Median for the colorbar and cuts [default: 1.6].
  --grid                                    Display a grid.
  --colorbar                                Display a colour bar.
  --horizontal                              Show the colour bar horizontally (ignored if colourbar not displayed).
  --mask                                    Set the display above the threshold value to be zero.
  --matrixfile                              Assume the input file is a pre-caculated matrix. In this case the heatmapresolution option will be ignored.
"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, MySQLdb, shutil, re, csv, subprocess
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile, transform, J2000toGalactic, calculateHeatMap
from math import sqrt
import numpy as n
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import matplotlib.colors as colors
import datetime
import os
import matplotlib.patheffects as path_effects
import copy
from astropy.stats import median_absolute_deviation

SMALL_SIZE = 14
MEDIUM_SIZE = 18
BIGGER_SIZE = 25
TINY_SIZE = 6
plt.rc('font', size=SMALL_SIZE)                   # controls default text sizes
plt.rc('axes', labelsize=TINY_SIZE)           # fontsize of the x and y labels
plt.rc('xtick', labelsize=TINY_SIZE)            # fontsize of the tick labels
plt.rc('ytick', labelsize=TINY_SIZE)            # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE - 1)               # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)   # fontsize of the figure title
plt.rcParams["font.family"] = "serif"
plt.rcParams['mathtext.fontset'] = 'dejavuserif'

def plotHeatMap(title, matrix, galacticCoords, obj, outputFile = None, heatMapResolution = 8, colorBarSpan = 2000.0, showGrid = False, showColorBar = False, median = None, showMask = False):
    """plotHeatMap.

    Args:
        title:
        matrix:
        galacticCoords:
        obj:
        outputFile:
        heatMapResolution:
        colorBarSpan:
        showGrid:
        showColorBar:
        median:
        showMask:
    """

#    if showMask:
#        # optional test - if array element > threshold/2, set it to zero.
#        matrix[matrix > colorBarSpan] = 0

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Set the gridding interval: here we use the major tick interval
    if showGrid:
        myInterval=8.
        loc = plticker.MultipleLocator(base=myInterval)
        ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)

        # Add the grid
        ax.grid(which='major', axis='both', linestyle='-', color="white")
        # Find number of gridsquares in x and y direction
        nx=abs(int(float(ax.get_xlim()[1]-ax.get_xlim()[0])/float(myInterval)))
        ny=abs(int(float(ax.get_ylim()[1]-ax.get_ylim()[0])/float(myInterval)))

    # Add the image
    plt.imshow(matrix, interpolation='none')
    ax.set_aspect('equal')

    ticks = n.arange(0,heatMapResolution,heatMapResolution/8) - 0.5
    ax.set_yticks(ticks)
    ax.set_xticks(ticks)

    # Turn off the axis labels
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white')

    plt.imshow(matrix, interpolation='none')
    ax.set_aspect('equal')

    if galacticCoords:
        t=ax.text(.5, .8, "l = %.2f" % galacticCoords[0], horizontalalignment='center', transform=ax.transAxes, color='white', size=10)
        t=ax.text(.5, .7, "b = %.2f" % galacticCoords[1], horizontalalignment='center', transform=ax.transAxes, color='white', size=10)
    if obj:
        t=ax.text(.5, .6, obj, horizontalalignment='center', transform=ax.transAxes, color='white', size=10)
    if median:
        t=ax.text(.5, .1, "median = %.1f" % median, horizontalalignment='center', transform=ax.transAxes, color='white', size=10)
        t.set_path_effects([path_effects.Stroke(linewidth=1.5,foreground='blue'), path_effects.Normal()])

    t=ax.text(.5, .9, title, horizontalalignment='center', transform=ax.transAxes, color='white', size=10)
    t.set_path_effects([path_effects.Stroke(linewidth=1.5,foreground='blue'), path_effects.Normal()])

    # This doesn't work yet!
    if showMask:
        #cmap = copy.copy(plt.cm.get_cmap("viridis"))
        my_cmap = plt.cm.get_cmap("viridis")
        my_cmap.set_over('black')

    #cbar = plt.colorbar(orientation='vertical', norm=colors.Normalize(vmin=0, vmax=10000))
    cbar = plt.colorbar(orientation='horizontal')
    cbar.mappable.set_clim(0, colorBarSpan)
    if not showColorBar:
        cbar.remove()
    if outputFile:
        plt.savefig(outputFile, dpi=600, bbox_inches='tight')
        plt.clf()
        plt.close()
    else:
        plt.show()

    return



def main():
    """main.
    """
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)
    options = Struct(**opts)

    dataRows = readGenericDataFile(options.filename, delimiter='\t')
    mat = {}
    if options.matrixfile:
        resolution = int(sqrt(len(dataRows)))
        if resolution not in [8, 16, 32, 64, 128, 256, 512]:
            print ("Invalid map resolution of %d" % (resolution))
        mat['matrix'] = n.array([int(x['ndet']) for x in dataRows]).reshape(resolution, resolution)
    else:
        mat = calculateHeatMap(dataRows, resolution = int(options.heatmapresolution))

    matrix = mat['matrix']

    # Flip the matrix up/down, because we are in pixel space now and y zero is top left.
    matrixFlipped = n.flip(matrix, 0)

    median = n.median(matrix)
    #median = median_absolute_deviation(matrix)
    stddev = n.std(matrix)
    mad = median_absolute_deviation(matrix)
    colorBarSpan = float(options.multiplier) * median
    count = n.count_nonzero(matrix > colorBarSpan)
    proportionPercentage = count/(matrix.shape[0]*matrix.shape[1]) * 100.0

    print (mad, median, stddev, median / stddev, colorBarSpan, float(options.multiplier) * stddev)

    print ("Mask percentage = %.2f%%" % (proportionPercentage))

    name = options.title
    if name is None and not options.matrixfile:
        name = os.path.basename(options.filename).split('.')[0] + ' (nobs = %d)' % len(mat['exps'])
    elif name is None and options.matrixfile and options.mask:
        name = "Mask = %.2f%%" % (proportionPercentage)

    plotHeatMap(name, matrixFlipped, None, None, outputFile = options.outputFile, heatMapResolution = int(options.heatmapresolution) , colorBarSpan = colorBarSpan, median = median, showGrid = options.grid, showColorBar = options.colorbar, showMask = options.mask)






if __name__=='__main__':
    main()

