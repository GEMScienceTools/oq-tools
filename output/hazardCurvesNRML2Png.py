#!/usr/bin/python

"""
Reads hazard curves files in NRML format and plot them using Matplotlib.
Required libraries are:
- lxml
- numpy
- matplotlib
"""

import sys
import argparse
from lxml import etree
import numpy
import matplotlib.pyplot as plt
import pylab

xmlNRML = '{http://openquake.org/xmlns/nrml/0.3}'
xmlGML = '{http://www.opengis.net/gml}'

def set_up_arg_parser():
    """
    Set up command line parser.
    """
    parser = argparse.ArgumentParser(description='Read hazard curves from NRML file and plot them using Matplotlib.'\
                    'Each curve is saved to a .PNG file.'\
                    'To run just type: python hazardCurvesNRML2Png.py --hazard-curves-file=/PATH/HAZARD_CURVES_FILE_NAME.xml')
    parser.add_argument('--hazard-curves-file',help='path to NRML hazard curves file',default=None)
    parser.add_argument('--ff',help='file format (eg. eps, png, jpg)',default='png')
    return parser

def parse_and_print_hazard_curves(hazard_curves_file,file_format):
    """
    Parse NRML hazard curves file. Plot each curve in a .PNG figure. 
    """
    parse_args = dict(source=hazard_curves_file)
    idx = 0
    hc_list = []
    min_poes = +1e10
    max_poes = -1e10
    for _, element in etree.iterparse(**parse_args):

        if element.tag == '%sIML' % xmlNRML:
            imls = numpy.array(element.text.split(),dtype=float)
        if element.tag == '%sHCNode' % xmlNRML:
            lon,lat,poes = parse_hazard_curve(element)
            hc_list.append({'idx':idx,'lon':lon,'lat':lat,'imls':imls,'poes':poes})
            min_poes = min(min_poes,min(poes))
            max_poes = max(max_poes,max(poes))
            idx += 1

    if min_poes < 1e-20:
        min_poes = 1.0e-6 

    for hc in hc_list:
        plot_curve(hc['idx'],hc['lon'],hc['lat'],
                hc['imls'],hc['poes'],file_format,[min_poes,max_poes])

def parse_hazard_curve(element):
    """
    Parse hazard curve node element, and return
    longitude, latitude, and probabilities of
    exceedance.
    """ 
    for e in element.iter():
        if e.tag == '%spos' % xmlGML:
            coords = str(e.text).split()
            lon = float(coords[0])
            lat = float(coords[1])
        if e.tag == '%spoE' % xmlNRML:
            poes = numpy.array(e.text.split(),dtype=float)
    return lon,lat,poes

def plot_curve(idx,lon,lat,imls,poes,file_format,mimx):
    """
    Plot curve using Matplotlib and save to .PNG file.
    """
    plt.loglog(imls,poes)
    plt.xlabel('Intensity measure levels')
    plt.ylabel('Probability of exceedance')
    plt.grid(True)
    plt.ylim(mimx)
    print mimx
    
    filename = '%03d_%.2f_%.2f.%s' % (idx,lon,lat,file_format)
    plt.savefig(filename, dpi=100)
    plt.clf()
    print 'saved hazard curve to file: %s' % filename

def main(argv):
    """
    Parse command line argument and performs requested action.
    """
    parser = set_up_arg_parser()
    args = parser.parse_args()

    if args.hazard_curves_file:
        parse_and_print_hazard_curves(
                args.hazard_curves_file,
                args.ff)
    else:
        parser.print_help()

if __name__=='__main__':

    main(sys.argv)
