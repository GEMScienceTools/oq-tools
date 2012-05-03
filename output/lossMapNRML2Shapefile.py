#!/usr/bin/python

"""
Convert loss map in NRML format to shapefile.
Supports NRML format 0.3.
Required libraries are:
- lxml
- pyshp
"""

import sys
import math
import argparse
import shapefile
from lxml import etree

xmlNRML = '{http://openquake.org/xmlns/nrml/0.3}'
xmlGML = '{http://www.opengis.net/gml}'

w = shapefile.Writer(shapefile.POINT)
w.field('VALUE','N',20,5)

def set_up_arg_parser():
	"""
	Set up command line parser.
	"""
	parser = argparse.ArgumentParser(description='Convert NRML format loss map file to shapefile.'\
					'To run just type: python lossMapNRML2Shapefile.py --loss-map-file=/PATH/LOSS_MAP_FILE_NAME.xml')
	parser.add_argument('--loss-map-file',help='path to NRML loss map file',default=None)
	return parser

def parse_loss_map_file(loss_map_file):
	"""
	Parse NRML loss map file.
	"""
	parse_args = dict(source=loss_map_file)

	lons = []
	lats = []
	data = []

	for _, element in etree.iterparse(**parse_args):

		if element.tag == '%sLMNode' % xmlNRML:
			lon,lat,value = parse_loss_map_node(element)
			lons.append(lon)
			lats.append(lat)
			data.append(value)
	
	return lons,lats,data

def parse_loss_map_node(element):
	"""
	Parse loss map node. Return longitude
	and latitude, and total loss (sum of
	losses from the different assets)
	"""
	total_value = 0.0
	for e in element.iter():
		if e.tag == '%spos' % xmlGML:
			coords = str(e.text).split()
			lon = float(coords[0])
			lat = float(coords[1])
		if e.tag == '%svalue' % xmlNRML:
			value = float(e.text)
			total_value += value
	return lon,lat,total_value

def serialize_data_to_shapefile(lons,lats,data,file_name):
	"""
	Serialize hazard map data to shapefile.
	"""
	for i in range(0,len(data)):
		w.point(lons[i],lats[i],0,0)
		w.record(round(data[i],5))
	w.save(file_name)

	print 'Shapefile saved to: %s.shp' % file_name	

def main(argv):
	"""
	Parse command line argument and performs requested action.
	"""
	parser = set_up_arg_parser()
	args = parser.parse_args()

	if args.loss_map_file:
		lons,lats,data = parse_loss_map_file(args.loss_map_file)
		serialize_data_to_shapefile(lons,lats,data,args.loss_map_file.split('.')[0])
	else:
		parser.print_help()

if __name__=='__main__':

	main(sys.argv)
