#!/usr/bin/env python
"""Plot an ATLAS detector heatmap from an input file - or import the plotHeatMap function. Input file needs headed rows called x and y.

Usage:
  %s <filename> [--outputFile=<file>] [--title=<title>] [--heatmapresolution=<heatmapresolution] [--delimiter=<delimiter>] [--medianMultiplier=<medianMultiplier>] [--grid] [--colorbar] [--mask] [--horizontal]
  %s (-h | --help)
  %s --version

Options:
  -h --help                                 Show this screen.
  --version                                 Show version.
  --outputFile=<file>                       Output file. If not defined, show plot.
  --title=<title>                           Plot title.
  --heatmapresolution=<heatmapresolution>   Heatmap resolution as a power of 2 between 8 and 512 [default: 128].
  --delimiter=<delimiter>                   Delimiter to use [default: \\t].
  --medianMultiplier=<medianMultiplier>     Multiplier for the Median for the colorbar and cuts [default: 1.2].
  --grid                                    Display a grid.
  --colorbar                                Display a colour bar.
  --horizontal                              Show the colour bar horizontally (ignored if colourbar not displayed).
  --mask                                    Set the display above the threshold value to be zero.
"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, MySQLdb, shutil, re, csv, subprocess
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile, transform, J2000toGalactic
import numpy as n
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import matplotlib.colors as colors
import datetime
import os
import matplotlib.patheffects as path_effects

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


def doPlot(options):

    heatMapResolution = int(options.heatmapresolution)
    if heatMapResolution not in [8, 16, 32, 64, 128, 256, 512]:
        print("Heatmap resolution should be 8,  16, 32, 64, 128, 256 or 512")

    #matrix = n.zeros((8,8), dtype=n.int)
    matrix = n.zeros((heatMapResolution,heatMapResolution), dtype=n.int)
    expmaps = {}

    dataRows = readGenericDataFile(options.filename, delimiter='\t')
    oldExpname = ''
    numberOfRows = 0
    #galacticCoords = None
    obj = None

    name = options.title

    exps = set()
    for row in dataRows:
        x = int(float(row['x'])/10559.0 * heatMapResolution)
        y = int((10559.0 - float(row['y']))/10559.0 * heatMapResolution)
        exps.add(row['obs'])

        if x >= 0 and y >= 0 and x < heatMapResolution and y < heatMapResolution:
            matrix[y][x] += 1

    medValue = n.median(matrix)

    colorBarSpan = float(options.medianMultiplier) * medValue

    if name is None:
        name = os.path.basename(options.filename).split('.')[0] + ' (nobs = %d)' % len(exps)

    plotHeatMap(name, matrix, None, None, outputFile = options.outputFile, heatMapResolution = heatMapResolution, colorBarSpan = colorBarSpan, median = medValue, showGrid = options.grid, showColorBar = options.colorbar, showMask = options.mask)


    return 0




def main():
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)
    options = Struct(**opts)

    doPlot(options)


if __name__=='__main__':
    main()


