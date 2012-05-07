#!/usr/bin/python

"""
Reads rupture model file in NRML fomat and converts it to shapefile.
Supports NRML format 0.3.
Required libraries are:
- lxml
- pyshp
- numpy
- nhlib
"""

import sys
import math
import argparse
import shapefile
from lxml import etree
import numpy
from nhlib.geo import _utils
from nhlib.geo.surface import SimpleFaultSurface, ComplexFaultSurface
from nhlib.geo import Point, Line

xmlNRML = '{http://openquake.org/xmlns/nrml/0.3}'
xmlGML = '{http://www.opengis.net/gml}'

w_poly = shapefile.Writer(shapefile.POLYGON)
w_poly.field('TECTONIC REGION TYPE','C','40')
w_poly.field('MAGNITUDE (Mw)','N',10,1)
w_poly.field('RAKE','N',10,1)

def set_up_arg_parser():
	"""
	Set up command line parser.
	"""
	parser = argparse.ArgumentParser(description='Convert NRML format rupture model file to shapefile.'\
					'The obtained shapefile contains rupture plane coordinates, tectonic region type, magnitude, rake'\
					'To run just type: '\
					'python ruptureModelNRML2Shapefile.py --rupture-model-file=/PATH/RUPTURE_MODEL_FILE_NAME.xml')
	parser.add_argument('--rupture-model-file',help='path to NRML rupture model file',default=None)
	return parser

def parse_rupture_model_file(rupture_model_file):
	"""
	Parse NRML simpleFaultRupture.
	"""
	parse_args = dict(source=rupture_model_file)

	for _, element in etree.iterparse(**parse_args):
		if element.tag == '%smagnitude' % xmlNRML:
			magnitude = float(element.text)
		if element.tag == '%stectonicRegion' % xmlNRML:
			tect_reg_type = element.text
		if element.tag == '%srake' % xmlNRML:
			rake = float(element.text)
		if element.tag == '%sposList' % xmlGML:
			posList = element.text
		if element.tag == '%sdip' % xmlNRML:
			dip = float(element.text)
		if element.tag == '%supperSeismogenicDepth' % xmlNRML:
			upper_seismo_depth = float(element.text)
		if element.tag == '%slowerSeismogenicDepth' % xmlNRML:
			lower_seismo_depth = float(element.text)

	polygon, area = get_polygon_area_from_simple_fault_data(posList,upper_seismo_depth,lower_seismo_depth,dip)

	return polygon, tect_reg_type, magnitude, rake

def get_polygon_area_from_simple_fault_data(posList,upper_seismo_depth,lower_seismo_depth,dip):

	fault_top_edge = posList.split()
	fault_top_edge = numpy.array(fault_top_edge,dtype=float).reshape(len(fault_top_edge)/3,3)
	fault_top_edge = Line([Point(v1,v2,v3) for v1,v2,v3 in fault_top_edge])

	az = fault_top_edge[0].azimuth(fault_top_edge[1]) + 180.0
	vertical_increment = - fault_top_edge[0].depth
	horizontal_increment = fault_top_edge[0].depth / numpy.tan(math.radians(dip))

	# compute fault trace from fault top edge as read from NRML
	fault_trace = []
	for point in fault_top_edge:
		fault_trace.append(point.point_at(horizontal_increment,vertical_increment,az))

	# create simple fault trace
	surf = SimpleFaultSurface.from_fault_data(Line(fault_trace), upper_seismo_depth,
			lower_seismo_depth, dip, mesh_spacing = 2.0)

	# extract fault boundary
	polygon = []
	fault_boundary = surf.get_mesh()._get_bounding_mesh()
	for lon,lat in zip(fault_boundary.lons,fault_boundary.lats):
		polygon.append([lon,lat])

	# compute area
	length = fault_top_edge.get_length()
	width = (lower_seismo_depth - upper_seismo_depth) / numpy.sin(math.radians(dip))

	return polygon, length * width

def serialize_data_to_shapefile(polygon,tect_reg_type,mag,rake,file_name):
	"""
	Serialize rupture data to shapefile.
	"""
	w_poly.poly(parts=[polygon])
	w_poly.record(tect_reg_type,round(mag,1),round(rake,1))

	w_poly.save(file_name)

	print 'Shapefile saved to: %s.shp' % file_name

def main(argv):
	"""
	Parse command line argument and performs requested action.
	"""
	parser = set_up_arg_parser()
	args = parser.parse_args()

	if args.rupture_model_file:
		polygon, tect_reg_type, mag, rake = parse_rupture_model_file(args.rupture_model_file)
		serialize_data_to_shapefile(polygon,tect_reg_type,mag,rake,args.rupture_model_file.split('.')[0])
	else:
		parser.print_help()

if __name__=='__main__':

	main(sys.argv)
