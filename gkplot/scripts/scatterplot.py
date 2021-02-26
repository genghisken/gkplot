#!/usr/bin/env python
"""Do a generic scatter plot.

Usage:
  %s <inputFile>... [--x=<x>] [--y=<y>] [--yerror=<yerror>] [--xlower=<xlower>] [--xupper=<xupper>] [--ylower=<ylower>] [--yupper=<yupper>] [--outputFile=<file>] [--threshold=<threshold>] [--log] [--xlabel=<xlabel>] [--ylabel=<ylabel>] [--xmajorticks=<xmajorticks>] [--xminorticks=<xminorticks>] [--ymajorticks=<ymajorticks>] [--yminorticks=<yminorticks>] [--plotlabel=<plotlabel>] [--plotlabelpos=<plotlabelpos>] [--panellabel=<panellabel>] [--panellabelpos=<panellabelpos>] [--alpha=<alpha>] [--pointsize=<pointsize>] [--mjdXaxis] [--addSecondaryTimeXAxis] [--grid] [--colour=<colour>] [--invert] [--tight] [--figsize=<figsize>] [--header=<header>] [--normalise] [--line] [--error] [--errorthick=<errorthick>]
  %s (-h | --help)
  %s --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --x=<x>                           Column to plot [default: MJD-OBS]
  --y=<y>                           Column to plot [default: SEEING]
  --yerror=<yerror>                 yerror to plot (ignored if --error flag is not set) [default: error]
  --xlower=<xlower>                 xlower limit [default: 57300]
  --xupper=<xupper>                 xupper limit of the bin [default: 58950]
  --ylower=<ylower>                 ylower limit [default: 2]
  --yupper=<yupper>                 yupper limit of the bin [default: 10]
  --outputFile=<file>               Output file. If not defined, show plot.
  --threshold=<threshold>           Plots a vertical dotted line.
  --xlabel=<xlabel>                 x label [default: ]
  --ylabel=<ylabel>                 y label [default: ]
  --plotlabel=<plotlabel>           Plot label (e.g. MLO ) [default: ]
  --plotlabelpos=<plotlabelpos>     Plot label position [default: 0.8]
  --panellabel=<panellabel>         Panel label (e.g. 'a)' ) [default: ]
  --panellabelpos=<panellabelpos>   Panel label position [default: 0.1]
  --xmajorticks=<xmajorticks>       x major ticks [default: 200.0]
  --xminorticks=<xminorticks>       x minor ticks [default: 20.0]
  --ymajorticks=<ymajorticks>       y major ticks [default: 1.0]
  --yminorticks=<yminorticks>       y minor ticks [default: 0.2]
  --colour=<colour>                 Specify colour or more than one colour separated commas with no spaces. [default: orange,cyan]
  --alpha=<alpha>                   transparency setting - comma separated no spaces if more than one alpha [default: 0.5]
  --pointsize=<pointsize>           point size [default: 0.5]
  --mjdXaxis                        X axis is MJD (so we can treat as a time axis)
  --addSecondaryTimeXAxis           Hence give option to add a time axis in date format.
  --header=<header>                 Assume no header file and collect it from the command line.
  --normalise                       Normalise the y axis.
  --line                            Line plot.
  --error                           Scatter plot with errorbars (ignored if --line selected).
  --errorthick=<errorthick>         Thickness of the error line and cap. [default: 0.5]
  --grid                            Add a grid
  --log                             Plot log(y) instead of y.
  --invert                          invert y axis.
  --tight                           tight layout.
  --figsize=<figsize>               figure size, comma separated, no spaces [default: 6,3]

E.g.:
   %s ~/atlas/dophot/ATLAS20ymv_dophot_o.txt ~/atlas/dophot/ATLAS20ymv_dophot_c.txt --x=mjd --y=mag --yerror=dminst --invert --xlower=59070 --xupper=59200 --ylower=15.5 --yupper=18.5 --tight --alpha=1 --pointsize=2 --xmajorticks=20 --xminorticks=2 --outputFile=/tmp/ATLAS20ymv_lc.png --error
"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, shutil, re, csv, subprocess
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import epoch2num
import matplotlib.dates as mdates

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
#months = mdates.MonthLocator(range(1, 13), bymonthday=1, interval=3)
monthsFmt = mdates.DateFormatter("%b %Y")
yearsFmt = mdates.DateFormatter('%Y')

import numpy as n

colours = ['orange', 'cyan']

SMALL_SIZE = 14
MEDIUM_SIZE = 18
BIGGER_SIZE = 25
TINY_SIZE = 12
plt.rc('font', size=SMALL_SIZE)                   # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)            # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)           # fontsize of the x and y labels
plt.rc('xtick', labelsize=TINY_SIZE)            # fontsize of the tick labels
plt.rc('ytick', labelsize=TINY_SIZE)            # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE - 1)               # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)   # fontsize of the figure title
plt.rcParams["font.family"] = "serif"
plt.rcParams['mathtext.fontset'] = 'dejavuserif'

def mjd2epoch(mjd):
    """
    Returns epoch in seconds given MJD.
    """
    return epoch2num((mjd + 2400000.5 - 2440587.5) * 86400.0)

def convert_ax2_to_epoch(ax1, ax2):
    """
    Update second axis according with first axis.
    """
    x1, x2 = ax1.get_xlim()
    ax2.set_xlim(mjd2epoch(x1), mjd2epoch(x2))
    #ax2.figure.canvas.draw()

def plotScatter(data, options):

    colours = options.colour.split(',')
    alphas = options.alpha.split(',')
    figsize = options.figsize.split(',')

    fig = plt.figure(figsize=(float(figsize[0]), float(figsize[1])))

    ax1 = fig.add_subplot(111)


    ax1 = fig.add_subplot(111)
    i = 0
    for d in data:
        if len(colours) == 1:
            colour = colours[0]
        else:
            colour = colours[i]

        if len(alphas) == 1:
            alpha = alphas[0]
        else:
            alpha = alphas[i]

        xarray = n.array(d['x'])
        yarray = n.array(d['y'])
        if options.error:
            yerrorarray = n.array(d['yerror'])

        if options.normalise:
            ymax = yarray.max()
            yarray = yarray/ymax

        if options.line:
            ax1.plot(xarray, yarray, alpha = float(alpha), color=colour)
        else:
            if options.error:
                ax1.errorbar(xarray, yarray, fmt='o', yerr=yerrorarray, color=colour, markersize = float(options.pointsize), alpha = float(alpha), elinewidth=float(options.errorthick), capsize=(float(options.errorthick)*2), capthick=float(options.errorthick))
                #ax1.errorbar(xarray, yarray, fmt='o', yerr=yerrorarray, color=colour, markersize = float(options.pointsize), fillstyle='full', alpha = float(alpha))
            else:
                ax1.scatter(xarray, yarray, marker='o', alpha = float(alpha), color=colour, s = float(options.pointsize), edgecolors='none')

        if options.mjdXaxis and options.addSecondaryTimeXAxis:
            # Assumes x axis is MJD
            ax2 = ax1.twiny()
            ax2.set_xlim(mjd2epoch(float(options.xlower)), mjd2epoch(float(options.xupper)))
            ax2.xaxis.set_major_locator(years)
            ax2.xaxis.set_major_formatter(yearsFmt)
            ax2.xaxis.set_minor_locator(months)
            ax2.set_xlabel('Date')
            #ax2.xaxis.set_minor_formatter(monthsFmt)
        i += 1

    ax1.set_ylabel(options.ylabel)
    for tl in ax1.get_yticklabels():
        tl.set_color('k')

    ax1.set_xlabel(options.xlabel)
    #ax1.set_title('Classifier performance.')
    #ax1.legend(loc=1)
    ax1.text(float(options.plotlabelpos), 0.95, options.plotlabel, transform=ax1.transAxes, va='top', size=MEDIUM_SIZE)
    ax1.text(float(options.panellabelpos), 0.95, options.panellabel, transform=ax1.transAxes, va='top', size=MEDIUM_SIZE, weight='bold')

    ml = MultipleLocator(float(options.xmajorticks))
    ax1.xaxis.set_major_locator(ml)
    ml = MultipleLocator(float(options.xminorticks))
    ax1.xaxis.set_minor_locator(ml)

    ml = MultipleLocator(float(options.ymajorticks))
    ax1.yaxis.set_major_locator(ml)
    ml = MultipleLocator(float(options.yminorticks))
    ax1.yaxis.set_minor_locator(ml)

    ax1.get_xaxis().set_tick_params(which='both', direction='out')
    ax1.set_xlim(float(options.xlower), float(options.xupper))
    ax1.set_ylim(float(options.ylower), float(options.yupper))

    if options.log:
        ax1.set_yscale('log')

    if options.invert:
        ax1.invert_yaxis() 

    if options.threshold is not None:
        ax1.axvline(x=float(options.threshold),color='k',linestyle='--')

    if options.grid:
        plt.grid(which='major', linestyle=':')
        plt.grid(which='minor', linestyle=':')

    if options.tight:
        plt.tight_layout()

    if options.outputFile is not None:
        plt.savefig(options.outputFile, bbox_inches='tight', pad_inches = 0.05, dpi=600)
    else:
        plt.show()


def doPlots(options):
    # There may be more than one inputFile
    allData = []
    fieldnames = None
    if options.header:
        fieldnames = options.header.split()
    for datafile in options.inputFile:
        data = {}
        dataRows = readGenericDataFile(datafile, delimiter=' ', fieldnames=fieldnames)

        x = []
        y = []
        yerror = []
        for row in dataRows:
            x.append(float(row[options.x]))
            y.append(float(row[options.y]))
            if options.error:
                yerror.append(float(row[options.yerror]))
        data['x'] = x
        data['y'] = y
        if options.error:
            data['yerror'] = yerror
        allData.append(data)

    plotScatter(allData, options)


def main():
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)
    options = Struct(**opts)

    doPlots(options)


if __name__=='__main__':
    main()


