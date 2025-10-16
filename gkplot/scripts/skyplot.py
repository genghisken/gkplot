#!/usr/bin/env python
"""Plot sky positions onto an Aitoff map of the sky.

Usage:
  %s <filename>... [--racol=<racol>] [--deccol=<deccol>] [--mjdcol=<mjdcol>] [--filtercol=<filtercol>] [--expnamecol=<expnamecol>] [--commentcol=<commentcol>] [--usepatches] [--alpha=<alpha>] [--outfile=<outfile>] [--tight] [--delimiter=<delimiter>] [--pointsize=<pointsize>] [--title=<title>] [--rectangular] [--fpshape=<fpshape>]
  %s (-h | --help)
  %s --version

Options:
  -h --help                    Show this screen.
  --version                    Show version.
  --racol=<racol>              Column that represents RA. [default: ra]
  --deccol=<deccol>            Column that represents declination. [default: dec]
  --mjdcol=<mjdcol>            Column that represents MJD. [default: mjd]
  --filtercol=<filtercol>      Column that represents filter. [default: filter]
  --expnamecol=<expnamecol>    Column that represents exposure name.
  --commentcol=<commentcol>    Column that represents a comment (e.g. a survey comment, for Pan-STARRS).
  --usepatches                 Plot patches (defined shapes), not points, e.g. ATLAS square footprints or Pan-STARRS circles mapped onto the sky.
  --rectangular                Use a rectangular footprint (equatorial mount, which is always oriented north-up). Otherwise assume circular.
  --outfile=<outfile>          Output file.
  --alpha=<alpha>              Transparency. [default: 0.1]
  --tight                      Tight layout.
  --delimiter=<delimiter>      Delimiter to use [default:  ]
  --pointsize=<pointsize>      Point size [default: 0.1]
  --title=<title>              Title for the plot.
  --fpshape=<fpshape>          Footprint shape. Use first value as radius. If two values supplied use one as x and the other as y. Comma separated, no spaces [default: 1.784]

E.g.:
  %s ~/atlas/dophot/small_area_fields_subset.txt --alpha=0.1 --usepatches --outfile=/tmp/test.png
"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
from gkutils.commonutils import Struct, readGenericDataFile, cleanOptions, sexToDec, getMJDFromSqlDate, GalactictoJ2000, EcliptictoJ2000, getDateFromMJD, transform
import csv

import numpy as np
import matplotlib.pyplot as pl
from matplotlib import colors
import matplotlib.patches as patches
import math


# ###########################################################################################
#                                         Main program
# ###########################################################################################

# Colors as defined in lightcurve.js

colors = ["#6A5ACD", #SlateBlue
          "#008000", #Green
          "#DAA520", #GoldenRod
          "#A0522D", #Sienna
          "#FF69B4", #HotPink
          "#DC143C", #Crimson
          "#008B8B", #DarkCyan
          "#FF8C00", #Darkorange
          "#FFD700", #Gold
          "#0000FF", #Blue
          "#4B0082", #Indigo
          "#800080", #Purple
          "#A52A2A", #Brown
          "#DB7093", #PaleVioletRed
          "#708090", #SlateGray
          "#800000", #Maroon
          "#B22222", #FireBrick
          "#9ACD32", #YellowGreen
          "#FA8072", #Salmon
          "#000000"]; #Black

def doPlot(options, objects, plotNumber = 111, alpha = 0.2, minMJD = 0.0, maxMJD = 60000.0, usePatches = False):

    gx = []
    gy = []
    rx = []
    ry = []
    ix = []
    iy = []
    zx = []
    zy = []
    yx = []
    yy = []
    wx = []
    wy = []
    cx = []
    cy = []
    ox = []
    oy = []

    for row in objects:
        try:
            ra = float(row[options.racol])
        except ValueError as e:
            ra = sexToDec(row[options.racol], ra=True)

        try:
            dec = float(row[options.deccol])
        except ValueError as e:
            dec = sexToDec(row[options.deccol], ra=False)

        if ra > 180.0:
            ra = 360.0 - ra
        else:
            ra = (-1.0) * ra

        try:
            mjd = float(row[options.mjdcol])
            # Maybe we got JD, not MJD - check.
            if mjd > 2400000.5:
                mjd = mjd - 2400000.5
        except ValueError as e:
            mjd = getMJDFromSqlDate(row[options.mjdcol])

        #if dec > -9.0 and dec < -8.0:
        #if mjd > 57053: # January 31st
        #if mjd > 57174: # June 1st
        if mjd is not None and mjd > minMJD and mjd < maxMJD:
            if row[options.filtercol][0] == 'g':
                print('g')
                gx.append(ra)
                gy.append(dec)
            elif row[options.filtercol][0] == 'r':
                print('r')
                rx.append(ra)
                ry.append(dec)
            elif row[options.filtercol][0] == 'i':
                print('i')
                ix.append(ra)
                iy.append(dec)
            elif row[options.filtercol][0] == 'z':
                print('z')
                zx.append(ra)
                zy.append(dec)
            elif row[options.filtercol][0] == 'y':
                yx.append(ra)
                yy.append(dec)
            elif row[options.filtercol][0] == 'w':
                wx.append(ra)
                wy.append(dec)
            elif row[options.filtercol][0] == 'c':
                cx.append(ra)
                cy.append(dec)
            elif row[options.filtercol][0] == 'o':
                ox.append(ra)
                oy.append(dec)
            #print (row[options.racol], row[options.deccol], row[options.expnamecol], row[options.commentcol], row[options.filtercol])

    degtorad = math.pi/180.

    gx = np.array(gx) * degtorad
    gy = np.array(gy) * degtorad

    rx = np.array(rx) * degtorad
    ry = np.array(ry) * degtorad

    ix = np.array(ix) * degtorad
    iy = np.array(iy) * degtorad

    zx = np.array(zx) * degtorad
    zy = np.array(zy) * degtorad

    yx = np.array(yx) * degtorad
    yy = np.array(yy) * degtorad

    wx = np.array(wx) * degtorad
    wy = np.array(wy) * degtorad

    cx = np.array(cx) * degtorad
    cy = np.array(cy) * degtorad

    ox = np.array(ox) * degtorad
    oy = np.array(oy) * degtorad


    fig2 = pl.figure(2)
    ax1 = fig2.add_subplot(plotNumber, projection="hammer")

    s = 5.4 * degtorad
    if ',' in options.fpshape:
        s = float(options.fpshape.split(',')[0])
    else:
        s = float(options.fpshape.split(',')[0])

    r = float(options.fpshape.split(',')[0]) * degtorad

    if usePatches:
        # Square exposures for ATLAS, circular ones for PS1
        for x,y in zip(gx,gy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[0], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[0], alpha = float(options.alpha)))
        for x,y in zip(rx,ry):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[1], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[1], alpha = float(options.alpha)))
        for x,y in zip(ix,iy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[2], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[2], alpha = float(options.alpha)))
        for x,y in zip(zx,zy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[3], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[3], alpha = float(options.alpha)))
        for x,y in zip(yx,yy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[4], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[4], alpha = float(options.alpha)))
        for x,y in zip(wx,wy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[5], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[5], alpha = float(options.alpha)))
        for x,y in zip(cx,cy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[6], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[6], alpha = float(options.alpha)))
        for x,y in zip(ox,oy):
            if options.rectangular:
                ax1.add_patch(patches.Rectangle((x-s/2.0, y-s/2.0), s/math.cos(y), s, color=colors[7], alpha = float(options.alpha)))
            else:
                ax1.add_patch(patches.Circle((x, y), r, color=colors[6], alpha = float(options.alpha)))
    else:
        ax1.scatter(gx,gy, alpha=float(options.alpha), edgecolors='none', color=colors[0], s = float(options.pointsize))
        ax1.scatter(rx,ry, alpha=float(options.alpha), edgecolors='none', color=colors[1], s = float(options.pointsize))
        ax1.scatter(ix,iy, alpha=float(options.alpha), edgecolors='none', color=colors[2], s = float(options.pointsize))
        ax1.scatter(zx,zy, alpha=float(options.alpha), edgecolors='none', color=colors[3], s = float(options.pointsize))
        ax1.scatter(yx,yy, alpha=float(options.alpha), edgecolors='none', color=colors[4], s = float(options.pointsize))
        ax1.scatter(wx,wy, alpha=float(options.alpha), edgecolors='none', color=colors[5], s = float(options.pointsize))
        ax1.scatter(cx,cy, alpha=float(options.alpha), edgecolors='none', color=colors[6], s = float(options.pointsize))
        ax1.scatter(ox,oy, alpha=float(options.alpha), edgecolors='none', color=colors[7], s = float(options.pointsize))

    gleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[0])
    rleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[1])
    ileg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[2])
    zleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[3])
    yleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[4])
    wleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[5])
    cleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[6])
    oleg = ax1.scatter(-10,-10, alpha=1.0, edgecolors='none', color=colors[7])

    #leg = ax1.legend(loc='upper right', scatterpoints = 1, prop = {'size':6})
    #leg = ax1.legend([gleg, rleg, ileg, zleg], ['g', 'r', 'i', 'z'], loc='upper right', scatterpoints = 1, prop = {'size':6})
    #leg = ax1.legend([gleg, rleg, ileg, zleg, yleg], ['g', 'r', 'i', 'z', 'y'], loc='upper right', scatterpoints = 1, prop = {'size':6})
    #leg = ax1.legend([gleg, rleg, ileg, zleg, yleg, wleg], ['g', 'r', 'i', 'z', 'y', 'w'], loc='upper right', scatterpoints = 1, prop = {'size':4})
    #leg = ax1.legend([gleg, rleg, ileg, zleg, yleg, wleg, cleg, oleg], ['g', 'r', 'i', 'z', 'y', 'w', 'c', 'o'], loc='upper right', scatterpoints = 1, prop = {'size':4})
    #leg = ax1.legend([wleg, yleg, cleg, gleg], ['MLO', 'HKO', 'STH', 'CHL'], loc='upper right', scatterpoints = 1, prop = {'size':4})

    #leg = ax1.legend([cleg, oleg], ['c', 'o'], loc='upper right', scatterpoints = 1, prop = {'size':4})

    #leg.get_frame().set_linewidth(0.0)
    #leg.get_frame().set_alpha(0.0)

    ax1.plot([-math.pi, math.pi], [0,0],'r-')
    ax1.plot([0,0],[-math.pi, math.pi], 'r-')

    labels = ['10h', '8h', '6h', '4h', '2h', '0h', '22h', '20h', '18h', '16h', '14h']
    ax1.axes.xaxis.set_ticklabels(labels)


    # Plot the galactic plane

    gp = []
    for l in range(0, 36000, 1):
        equatorialCoords = transform([l/100.0, 0.0], GalactictoJ2000)
        gp.append(equatorialCoords)


    ras = []
    decs = []
    for row in gp:
        ra, dec = row
        if ra > 180.0:
            ra = 360.0 - ra
        else:
            ra = (-1.0) * ra

        ras.append(ra)
        decs.append(dec)


    ras = np.array(ras) * degtorad
    decs = np.array(decs) * degtorad

    ax1.plot(ras,decs, 'k.', markersize=1.0)

    # Plot the ecliptic plane


    ep = []
    for l in range(0, 36000, 1):
        equatorialCoords = transform([l/100.0, 0.0], EcliptictoJ2000)
        ep.append(equatorialCoords)


    ras = []
    decs = []
    for row in ep:
        ra, dec = row
        if ra > 180.0:
            ra = 360.0 - ra
        else:
            ra = (-1.0) * ra

        ras.append(ra)
        decs.append(dec)


    ras = np.array(ras) * degtorad
    decs = np.array(decs) * degtorad

    ax1.plot(ras,decs, 'b.', markersize=1.0)


    #ax1.axes.yaxis.set_ticklabels([])
    # plot celestial equator
    #ax1.plot(longitude2,latitude2,'g-')

    #for i in range(0,6):
    #    ax1.text(xrad[i], yrad[i], lab[i])

    if options.title:
        #pl.title("%s" % options.title, color='b', fontsize=12)
        pl.title("%s" % getDateFromMJD(float(options.title)).split(' ')[0], color='b', fontsize=12)
    pl.grid(True)
    return pl


def plotHammerProjection(options, filename, objects, alpha = 0.2, minMJD = 0.0, maxMJD = 70000.0, usePatches = False):

    print (maxMJD -1, maxMJD)
    print (minMJD, maxMJD)
#    pl = doPlot(options, objects, plotNumber = 212, alpha = alpha, minMJD = maxMJD - 1, maxMJD = maxMJD)
    pl = doPlot(options, objects, plotNumber = 111, alpha = alpha, minMJD = minMJD, maxMJD = maxMJD, usePatches = usePatches)
    #pl = doPlot(options, objects, plotNumber = 212, alpha = alpha, minMJD = 57168, maxMJD = 57169)

    if options.tight:
        pl.tight_layout()

    if options.outfile:
        pl.savefig(options.outfile, dpi=600)
        pl.clf()
    else:
        pl.show()
        #pl.savefig(filename + '_%s' % str(maxMJD) + '.png', dpi=600)



def doStats(options, filename, objects):
    """Do some stats on the list of objects - e.g. How many occurrences of something"""

    from collections import Counter

    mjds = []
    fp = {}
    for row in objects:
        try:
            mjd = float(row['mjd'])
        except ValueError as e:
            mjd = getMJDFromSqlDate(row['mjd'])

        wholeMJD = int(mjd)
        mjds.append(wholeMJD)

        try:
            fp[wholeMJD].append(row[options.expnamecol])
        except KeyError as e:
            fp[wholeMJD] = [row[options.expnamecol]]

    # Count the number of exposures per night
    mjdFrequency = Counter(mjds)

    for k,v in mjdFrequency.items():
        print (k,v)

    print ()
    # Now count the frequency of fpa_object per night.  This will tell us how much
    # sky is ACTUALLY covered each night.

    for k,v in fp.items():
        footprintFrequency = Counter(fp[k])
        print (k, len(footprintFrequency))



def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    options = Struct(**opts)



    # maxMJD = 57169 = 27th May 2015.  GPC1 out of sync after that.
    # minMJD = 57053 = 31st January 2015.
    # minMJD = 56991 = 30th November 2014 - when we restarted the survey

    # plotHammerProjection(options, filename, objectsList, alpha=0.7, minMJD = 57032.0, maxMJD = 57169.0)
    # plotHammerProjection(options, filename, objectsList, alpha=0.2, minMJD = 56991.0, maxMJD = 57169.0)
    # plotHammerProjection(options, filename, objectsList, alpha=0.7, minMJD = 0.0, maxMJD = 57169.0)
    #for mjd in range(55230, 57169):
    #    plotHammerProjection(options, filename, objectsList, alpha=0.2, minMJD = 55229, maxMJD = mjd)

    # For object plots min MJD is 56444 and (current) max is 57410

#    for mjd in range(56443, 57411):
#        plotHammerProjection(options, filename, objectsList, alpha=0.4, minMJD = 56443, maxMJD = mjd)

    # 2016-06-23 KWS Added code to use "patches" to plot accurate ATLAS and PS1 footprints. We don't
    #                want to use patches if we are plotting object locations.
#    jan01 = 57388
#    feb01 = 57419
#    mar01 = 57448
#    apr01 = 57479
#    may01 = 57509
#    jun01 = 57540
#    jul01 = 57570
#    aug01 = 57601
#    sep01 = 57632
#    oct01 = 57662

#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = jan01, maxMJD = feb01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = feb01, maxMJD = mar01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = mar01, maxMJD = apr01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = apr01, maxMJD = may01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = may01, maxMJD = jun01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = jun01, maxMJD = jul01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = jul01, maxMJD = aug01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = aug01, maxMJD = sep01)
#    plotHammerProjection(options, filename, objectsList, alpha=0.02, usePatches = True, minMJD = sep01, maxMJD = oct01)
    #alpha = 0.002

    print(options)
    print("Delimiter = ", options.delimiter)
    for filename in options.filename:
        objectsList = readGenericDataFile(filename, delimiter=options.delimiter)
        plotHammerProjection(options, filename, objectsList, alpha=float(options.alpha), usePatches = options.usepatches)
    

    #doStats(options, filename, objectsList)


if __name__ == '__main__':
    main()
