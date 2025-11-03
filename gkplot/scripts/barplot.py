#!/usr/bin/env python
"""Plot generic bar chart.

Usage:
  %s <filename> [--outputFile=<file>] [--title=<title>] [--x=<x>] [--y=<y>] [--xlabel=<xlabel>] [--ylabel=<ylabel>] [--xlower=<xlower>] [--xupper=<xupper>] [--ylower=<ylower>] [--yupper=<yupper>] [--delimiter=<delimiter]
  %s (-h | --help)
  %s --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --outputFile=<file>               Output file. If not defined, show plot.
  --title=<title>                   Plot title
  --x=<x>                           Column to plot [default: detector]
  --y=<y>                           Column to plot [default: ndet]
  --xlabel=<xlabel>                 x label [default: ]
  --ylabel=<ylabel>                 y label [default: ]
  --xlower=<xlower>                 xlower limit
  --xupper=<xupper>                 xupper limit
  --ylower=<ylower>                 ylower limit
  --yupper=<yupper>                 yupper limit
  --delimiter=<delimiter>           Delimiter to use [default: ,].
"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, MySQLdb, shutil, re, csv, subprocess
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as n

SMALL_SIZE = 14
MEDIUM_SIZE = 18
BIGGER_SIZE = 25
TINY_SIZE = 6
plt.rc('font', size=SMALL_SIZE)                   # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)            # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)           # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)            # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)            # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE - 1)               # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)   # fontsize of the figure title
plt.rcParams["font.family"] = "serif"
plt.rcParams['mathtext.fontset'] = 'dejavuserif'


def plotBarChart(options, data):
    # Build a dictionary of detector index → count
    dataBars = {int(row[options.x]): int(row[options.y]) for row in data}

    max_det = max(dataBars.keys())
    detectors = list(range(max_det + 3))
    counts = [dataBars.get(i, 0) for i in detectors]

    # Set the figure size for 16:9 aspect ratio
    fig, ax1 = plt.subplots(figsize=(23, 9))

    ax1.bar(detectors, counts, color="SkyBlue", edgecolor='black', linewidth=0.0, align="center")

    # Label every 10th detector
    tick_step = 10
    ax1.set_xticks(n.arange(0, max_det + 3, tick_step))
    ax1.set_xlim(-1, max_det + 3)

    ax1.set_ylabel(options.ylabel)
    ax1.set_xlabel(options.xlabel)
    if hasattr(options, "title") and options.title is not None:
        ax1.set_title(options.title)

    plt.tight_layout()

    if options.outputFile is not None:
        plt.savefig(options.outputFile, dpi=75)
    else:
        plt.show()


def doPlots(options):
    data = []
    dataRows = readGenericDataFile(options.filename, delimiter=options.delimiter)
    for row in dataRows:
        data.append(row)

    plotBarChart(options, data)


def main():
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)
    options = Struct(**opts)

    doPlots(options)


if __name__=='__main__':
    main()


