#!/usr/bin/env python
#
# wcml_hm_gen.py is part of wcml ( WiFi Coverage Mapper Live ), maintained at
# https://github.com/ntekpelek/wcml
# Released under GNU GPL v2
# Copyright (C) 2015 Adam Piontek
#
import os
import matplotlib
matplotlib.use('Agg')
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import json
import shlex
import sys
import argparse
import tempfile


def _to_int_array(arg):
    _tmp = arg.split(',')
    res = []
    for item in _tmp:
        res.append(int(item))
    return res


def _mirror_y(points, height):
    res = []
    for point in points:
        m_point = height - point
        res.append(m_point)
    return res


def generate(json_in, png_out):
    """Generates heatmap
    json_in -- JSON input file
    png_out - heatmap PNG file
    """
    try:
        # read JSON data from file
        surv_data = json.loads(json.load(open(json_in)))

        xpoints = []
        ypoints = []
        signals = []
        # convert values to in arrays
        meta_set = surv_data['survey']['meta']
        points = surv_data['survey']['points']
        # get settings value ( width, height )
        fplanwidth = meta_set['floorPlanWidth']
        fplanheight = meta_set['floorPlanHeight']

        for p in points:
            xpoints.append(p['posX'])
            ypoints.append(p['posY'])
            signals.append(p['signalSta'])

        ypoints = _mirror_y(ypoints, fplanheight)

        xi = np.linspace(0, int(fplanwidth), 200)
        yi = np.linspace(0, int(fplanheight), 200)
        zi = griddata(xpoints, ypoints, signals, xi, yi)
        mycdict = {'red': ((0.0, 1.0, 1.0),
            (0.4, 1.0, 1.0),
            (1.0, 0.0, 0.0)),

            'green': ((0.0, 0.0, 0.0),
            (0.1, 0.2, 0.2),
            (0.45, 0.9, 0.9),
            (1.0, 1.0, 1.0)),

            'blue': ((0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0))
        }
        mycmap = matplotlib.colors.LinearSegmentedColormap('MyCmap', mycdict)
        CS = plt.contour(xi, yi, zi, 15, linewidths=0.8,
                         colors='k', levels=[-72])
        plt.contourf(xi, yi, zi, np.linspace(-90, -42, 33),
                     cmap=mycmap, extend='both')
        # remove surrounding empty space
        fig = plt.gcf()
        fig.patch.set_visible(False)
        a = fig.gca()
        a.set_frame_on(False)
        a.set_xticks([])
        a.set_yticks([])
        plt.axis('off')
        # save to .svg
        svg_tmp = tempfile.NamedTemporaryFile(delete=False)
        fig.savefig(svg_tmp, frameon=False, dpi=200, transparent=True,
                    format='svg', pad_inches=0,
                    bbox_inches="tight", bbox_extra_artists=[])
        svg_tmp.close()
        # prepare convertion command
        cmdline = '/usr/bin/rsvg-convert -w %s -h %s %s -o %s' % (fplanwidth,
            fplanheight,
            svg_tmp.name, # SVG input file
            png_out ) # output png
        args = shlex.split(cmdline)
        # convert svg to png
        subprocess.call(args)
        os.remove(svg_tmp.name)

    except IOError:
        print 'IOError'
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'wcml heatmap generator')
    parser.add_argument("-i", "--input", help='JSON input file')
    parser.add_argument("-o", "--output", help='PNG output')
    args = parser.parse_args()

    # check arguments
    if ( args.input == None or args.output == None ):
        print 'Supply required arguements'
        sys.exit(1)
    else:
        generate(args.input, args.output)
