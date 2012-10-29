#!/usr/bin/python

"""
Read loss (and loss-ratio) curves files in NRML format and plot them using Matplotlib.
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

xmlNRML = '{http://openquake.org/xmlns/nrml/0.3}'
xmlGML = '{http://www.opengis.net/gml}'

def set_up_arg_parser():
	"""
	Set up command line parser.
	"""
	parser = argparse.ArgumentParser(description='Read loss (loss-ratio) curves from NRML file and plot them using Matplotlib.'\
					'Each curve is saved to a .PNG file.'\
					'To run just type: python lossCurvesNRML2Png.py --loss-curves-file=/PATH/LOSS_CURVES_FILE_NAME.xml')
	parser.add_argument('--loss-curves-file',help='path to NRML loss curves file',default=None)
	return parser

def parse_and_print_loss_curves(loss_curves_file):
	"""
	Parse NRML loss curves file. Plot each curve in a .PNG figure. 
	"""
	parse_args = dict(source=loss_curves_file)

	for _, element in etree.iterparse(**parse_args):

		if element.tag == '%sasset' % xmlNRML:
			ID,x_label,lon,lat,loss,poe = parse_asset(element)
			print loss, poe
			plot_curve(ID,x_label,lon,lat,loss,poe)

def parse_asset(element):
	"""
	Parse asset element, and return
	longitude, latitude, losses and poes.
	"""	
	ID = element.get('%sid' % xmlGML)
	for e in element.iter():
		if e.tag == '%spos' % xmlGML:
			coords = str(e.text).split()
			lon = float(coords[0])
			lat = float(coords[1])
		if e.tag == '%slossCurve' % xmlNRML:
			loss = numpy.array(e.find('%sloss' % xmlNRML).text.split(),dtype=float)
			poe = numpy.array(e.find('%spoE' % xmlNRML).text.split(),dtype=float)
			x_label = 'loss'
		if e.tag == '%slossRatioCurve' % xmlNRML:
			loss = numpy.array(e.find('%slossRatio' % xmlNRML).text.split(),dtype=float)
			poe = numpy.array(e.find('%spoE' % xmlNRML).text.split(),dtype=float)
			x_label = 'loss ratio'
	return ID,x_label,lon,lat,loss,poe

def plot_curve(ID,x_label,lon,lat,loss,poe):
	"""
	Plot curve using Matplotlib and save to .PNG file.
	"""
	plt.loglog(loss,poe)
	plt.xlabel(x_label)
	plt.ylabel('Probability of exceedance')
	plt.grid(True)
	
	filename = '%s_%s_%s.png' % (ID,lon,lat)
	plt.savefig(filename, dpi=100)
	plt.clf()
	print 'saved loss/loss-ratio curve to file: %s' % filename

def main(argv):
	"""
	Parse command line argument and performs requested action.
	"""
	parser = set_up_arg_parser()
	args = parser.parse_args()

	if args.loss_curves_file:
		parse_and_print_loss_curves(args.loss_curves_file)
	else:
		parser.print_help()

if __name__=='__main__':

	main(sys.argv)
