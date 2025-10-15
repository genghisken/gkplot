#!/usr/bin/env python
"""Do a generic scatter plot.

Usage:
  %s <inputFile>... [--x=<x>] [--y=<y>] [--yerror=<yerror>] [--xlower=<xlower>] [--xupper=<xupper>] [--ylower=<ylower>] [--yupper=<yupper>] [--outputFile=<file>] [--threshold=<threshold>] [--log] [--xlabel=<xlabel>] [--ylabel=<ylabel>] [--xmajorticks=<xmajorticks>] [--xminorticks=<xminorticks>] [--ymajorticks=<ymajorticks>] [--yminorticks=<yminorticks>] [--plotlabel=<plotlabel>] [--plotlabelpos=<plotlabelpos>] [--panellabel=<panellabel>] [--panellabelpos=<panellabelpos>] [--alpha=<alpha>] [--pointsize=<pointsize>] [--mjdXaxis] [--addSecondaryTimeXAxis] [--grid] [--colour=<colour>] [--invert] [--tight] [--figsize=<figsize>] [--header=<header>] [--normalise] [--line] [--linewidth=<linewidth>] [--error] [--errorthick=<errorthick>] [--delimiter=<delimiter>] [--legend] [--legendlabels=<legendlabels>] [--equalaspect] [--title=<title>]
  %s (-h | --help)
  %s --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --x=<x>                           Column to plot [default: MJD-OBS]
  --y=<y>                           Column to plot [default: SEEING]
  --yerror=<yerror>                 yerror to plot (ignored if --error flag is not set) [default: error]
  --xlower=<xlower>                 xlower limit
  --xupper=<xupper>                 xupper limit
  --ylower=<ylower>                 ylower limit
  --yupper=<yupper>                 yupper limit
  --outputFile=<file>               Output file. If not defined, show plot.
  --threshold=<threshold>           Plots a vertical dotted line.
  --xlabel=<xlabel>                 x label [default: ]
  --ylabel=<ylabel>                 y label [default: ]
  --plotlabel=<plotlabel>           Plot label (e.g. MLO ) [default: ]
  --plotlabelpos=<plotlabelpos>     Plot label position [default: 0.8]
  --panellabel=<panellabel>         Panel label (e.g. 'a)' ) [default: ]
  --panellabelpos=<panellabelpos>   Panel label position [default: 0.1]
  --xmajorticks=<xmajorticks>       x major ticks
  --xminorticks=<xminorticks>       x minor ticks
  --ymajorticks=<ymajorticks>       y major ticks
  --yminorticks=<yminorticks>       y minor ticks
  --colour=<colour>                 Specify colour or more than one colour separated commas with no spaces. [default: orange,cyan]
  --alpha=<alpha>                   transparency setting - comma separated no spaces if more than one alpha [default: 0.5]
  --pointsize=<pointsize>           point size [default: 0.5]
  --mjdXaxis                        X axis is MJD (so we can treat as a time axis)
  --addSecondaryTimeXAxis           Hence give option to add a time axis in date format.
  --header=<header>                 Assume no header file and collect it from the command line.
  --normalise                       Normalise the y axis.
  --line                            Line plot.
  --linewidth=<linewidth>           Line width [default: 0.5].
  --error                           Scatter plot with errorbars (ignored if --line selected).
  --errorthick=<errorthick>         Thickness of the error line and cap. [default: 0.5]
  --grid                            Add a grid
  --legend                          Add a legend
  --legendlabels=<legendlabels>     Legend labels. Comma separated, no spaces.
  --log                             Plot log(y) instead of y.
  --invert                          invert y axis.
  --tight                           tight layout.
  --figsize=<figsize>               figure size, comma separated, no spaces [default: 6,3]
  --delimiter=<delimiter>           Delimiter to use [default: ,].
  --equalaspect                     Set the aspect ratio to equal.
  --title=<title>                   Plot title.

E.g.:
   %s ~/atlas/dophot/ATLAS20ymv_dophot_o.txt ~/atlas/dophot/ATLAS20ymv_dophot_c.txt --x=mjd --y=mag --yerror=dminst --invert --xlower=59070 --xupper=59200 --ylower=15.5 --yupper=18.5 --tight --alpha=1 --pointsize=2 --xmajorticks=20 --xminorticks=2 --outputFile=/tmp/ATLAS20ymv_lc.png --error

   %s ~/atlas/dophot/galactic_centre_vs_o.txt --x=mjd --y=mag --yerror=dminst --invert --xlower=57700 --xupper=59200 --ylower=12.5 --yupper=18.5 --tight --alpha=1 --pointsize=2 --xmajorticks=200 --xminorticks=20 --outputFile=/tmp/galactic_centre_lc.png --error

   %s /tmp/tAT2023plg_20231105_Gr13_Free_slit1.0_1_f.asci --x='wavelength' --y='flux' --xlower=3500 --xupper=9500 --ylower=-0.3 --yupper=1.1 --outputFile=/tmp/AT2023plg.jpeg --xlabel=wavelength --ylabel='normalised flux' --xmajorticks=500 --xminorticks=100 --ymajorticks=0.1 --yminorticks=0.01 --header='wavelength flux' --normalise --line --linewidth=0.25 --colour=black --alpha=1.0 --delimiter=' ' --title=AT2023plg

   %s ~/atlas/dophot/232.6801_21.1287_o.dph ~/atlas/dophot/232.6801_21.1287_c.dph ~/atlas/dophot/Q2326801+211287_o.lc ~/atlas/dophot/Q2326801+211287_c.lc --x=mjd --y=m --yerror=dminst --invert --xlower=57070 --xupper=60750 --ylower=14 --yupper=20.5 --tight --alpha=1 --xmajorticks=200 --xminorticks=20 --error --delimiter=' ' --outputFile=/tmp/232.6801_21.1287.dph.png --colour=orange,cyan,red,blue

   %s /Users/kws/soxs-workspace-20250604/reduced/2025-06-04/soxs-stare/20250605T075734_VIS_1X1_1_STARE_SLIT1.0_1800.0S_SOXS_SN2025ML_EXTRACTED_MERGED.txt /Users/kws/soxs-workspace-20250604/reduced/2025-06-04/soxs-stare/20250605T083853_VIS_1X1_1_STARE_SLIT1.0_2400.0S_SOXS_SN2025ML_EXTRACTED_MERGED.txt /Users/kws/soxs-workspace-20250604/reduced/2025-06-04/soxs-stare/20250605T092314_VIS_1X1_1_STARE_SLIT5.0_2400.0S_SOXS_SN2025ML_EXTRACTED_MERGED.txt --x=WAVE --y=FLUX_COUNTS --line --linewidth=0.1 --colour=black,red,blue --alpha=1.0,1.0,1.0 --xlabel='wavelength (nm)' --ylabel=flux --delimiter=' ' --title=SN2025mlo --legend --legendlabels='1800s slit=1.0','2400s slit=1.0','2400s slit=5.0'
"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, shutil, re, csv, subprocess
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import AutoMinorLocator
#from matplotlib.dates import epoch2num
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
plt.rc('axes', titlesize=TINY_SIZE)            # fontsize of the axes title
plt.rc('axes', labelsize=TINY_SIZE)           # fontsize of the x and y labels
plt.rc('xtick', labelsize=TINY_SIZE)            # fontsize of the tick labels
plt.rc('ytick', labelsize=TINY_SIZE)            # fontsize of the tick labels
plt.rc('legend', fontsize=TINY_SIZE)               # legend fontsize
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

    if options.legend:
        plotlabels = options.legendlabels.split(',')

    #ax1 = fig.add_subplot(111)

    ax1 = fig.add_subplot(111)
    i = 0
    legends = []
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
            label=None
            if options.legend:
                label = plotlabels[i]
            ax1.plot(xarray, yarray, alpha = float(alpha), color=colour, linewidth=float(options.linewidth), label = label)
        else:
            if options.error:
                legends.append(ax1.errorbar(xarray, yarray, fmt='o', yerr=yerrorarray, color=colour, markersize = float(options.pointsize), alpha = float(alpha), elinewidth=float(options.errorthick), capsize=(float(options.errorthick)*2), capthick=float(options.errorthick)))
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
    if options.title:
        ax1.set_title(options.title)

    ax1.text(float(options.plotlabelpos), 0.95, options.plotlabel, transform=ax1.transAxes, va='top', size=MEDIUM_SIZE)
    ax1.text(float(options.panellabelpos), 0.95, options.panellabel, transform=ax1.transAxes, va='top', size=MEDIUM_SIZE, weight='bold')

    if options.xmajorticks and options.xminorticks:
        ml = MultipleLocator(float(options.xmajorticks))
        ax1.xaxis.set_major_locator(ml)
        ml = MultipleLocator(float(options.xminorticks))
        ax1.xaxis.set_minor_locator(ml)
    else:
        ml = AutoMinorLocator(10)
        ax1.xaxis.set_minor_locator(ml)

    if options.ymajorticks and options.yminorticks:
        ml = MultipleLocator(float(options.ymajorticks))
        ax1.yaxis.set_major_locator(ml)
        ml = MultipleLocator(float(options.yminorticks))
        ax1.yaxis.set_minor_locator(ml)
    else:
        ml = AutoMinorLocator(10)
        ax1.yaxis.set_minor_locator(ml)

    ax1.get_xaxis().set_tick_params(which='both', direction='out')

    if options.xlower and options.xupper:
        ax1.set_xlim(float(options.xlower), float(options.xupper))

    if options.ylower and options.yupper:
        ax1.set_ylim(float(options.ylower), float(options.yupper))

    if options.equalaspect:
        ax1.axes.set_aspect('equal')

    if options.log:
        ax1.set_yscale('log')

    if options.invert:
        ax1.invert_yaxis() 

    if options.threshold is not None:
        ax1.axvline(x=float(options.threshold),color='k',linestyle='--')

#    if options.legend:
#        ax1.legend(legends, options.legendlabels.split(','), loc='upper right', scatterpoints = 1, prop = {'size':4})

    if options.legend:
        leg = ax1.legend(loc='upper right', scatterpoints = 1)
        # Thicken the lines in the legend
        for legend_line in leg.legend_handles:
            legend_line.set_linewidth(1)


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
        fieldnames = options.header.split(options.delimiter)
    for datafile in options.inputFile:
        data = {}
        dataRows = readGenericDataFile(datafile, delimiter=options.delimiter, fieldnames=fieldnames)

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


