#!/usr/bin/python

"""
Reads source model file in NRML fomat and converts it to shapefile.
Supports NRML format 0.3.
Required libraries are:
- lxml
- pyshp
- numpy
- nhlib
- shapely
"""

import sys
import math
import argparse
import shapefile
from lxml import etree
import numpy
import shapely
from nhlib.geo import _utils
from nhlib.geo.surface import SimpleFaultSurface, ComplexFaultSurface
from nhlib.geo import Point, Line

xmlNRML = '{http://openquake.org/xmlns/nrml/0.3}'
xmlGML = '{http://www.opengis.net/gml}'

w_point = shapefile.Writer(shapefile.POINT)
w_point.field('ID','C','40')
w_point.field('NAME','C','40')
w_point.field('MAX MAG (Mw)','N',10,1)
w_point.field('TOT_OCC_RATE','N',16,14)

w_poly = shapefile.Writer(shapefile.POLYGON)
w_poly.field('ID','C','40')
w_poly.field('NAME','C','40')
w_poly.field('MAX MAG (Mw)','N',10,1)
w_poly.field('TOT_OCC_RATE','N',16,14)

def set_up_arg_parser():
	"""
	Set up command line parser.
	"""
	parser = argparse.ArgumentParser(description='Convert NRML format source model file to shapefile.'\
					'The obtained shapefile contains for each source a record storing'\
					' the following information: ID, NAME, MAXIMUM MAGNITUDE, TOTAL OCCURRENCE RATE'\
					' (per year and per unit area). NOTE: for point sources the total occurrence rate'\
					' is given per year, but not per unit area, because rates are concentrated on a single point.'\
					'To run just type: python sourceModelNRML2Shapefile.py --source-model-file=/PATH/SOURCE_MODEL_FILE_NAME.xml')
	parser.add_argument('--source-model-file',help='path to NRML source model file',default=None)
	return parser

def parse_source_model_file(source_model_file):
	"""
	Parse NRML format source model file
	and returns list of source data,
	each source data being a dictionary:
	src_data = {'ID':id,'NAME':name,'POINT',point,'POLYGON':polygon,'MAX_MAG','TOT_OCC_RATE'}
	"""
	data = []
	parse_args = dict(source=source_model_file)

	for _, element in etree.iterparse(**parse_args):
		if element.tag == '%sareaSource' % xmlNRML:
			ID,name,point,polygon,max_mag,tot_occ_rate = parse_area_source(element)
			src_data = {'ID':ID,
				'NAME':name,
				'POINT':point,
				'POLYGON':polygon,
				'MAX_MAG':round(max_mag,1),
				'TOT_OCC_RATE':round(tot_occ_rate,14)}
			data.append(src_data)
		if element.tag == '%spointSource' % xmlNRML:
			ID,name,point,polygon,max_mag,tot_occ_rate = parse_point_source(element)
			src_data = {'ID':ID,
				'NAME':name,
				'POINT':point,
				'POLYGON':polygon,
				'MAX_MAG':round(max_mag,1),
				'TOT_OCC_RATE':round(tot_occ_rate,14)}
			data.append(src_data)
		if element.tag == '%ssimpleFaultSource' % xmlNRML:
			ID,name,point,polygon,max_mag,tot_occ_rate = parse_simple_fault_source(element)
			src_data = {'ID':ID,
				'NAME':name,
				'POINT':point,
				'POLYGON':polygon,
				'MAX_MAG':round(max_mag,1),
				'TOT_OCC_RATE':round(tot_occ_rate,14)}
			data.append(src_data)
		if element.tag == '%scomplexFaultSource' % xmlNRML:
			ID,name,point,polygon,max_mag,tot_occ_rate = parse_complex_fault_source(element)
			src_data = {'ID':ID,
				'NAME':name,
				'POINT':point,
				'POLYGON':polygon,
				'MAX_MAG':round(max_mag,1),
				'TOT_OCC_RATE':round(tot_occ_rate,14)}
			data.append(src_data)

	return data

def parse_area_source(element):
	"""
	Parse NRML area source element, and extract:
	ID, name, area boundary (as polygon), maximum magnitude (the maximum among all
	the maximum magnitudes from all the FMD defined),
	total occurrence rate (by summing occurrence rates from all the FMD defined)
	"""
	ID = element.get('%sid' % xmlGML)
	for e in element.iter():
		if e.tag == '%sname' % xmlGML:
			name = e.text
		if e.tag == '%sposList' % xmlGML:
			polygon = get_polygon_from_2DLinestring(e.text)
		if e.tag == '%sruptureRateModel' % xmlNRML:
			max_mag, tot_occ_rate = parse_rupture_rate_model(e)

	# normalize occurrence rate by polygon area
	tot_occ_rate = tot_occ_rate / get_polygon_area(polygon)

	return ID,name,None,polygon,max_mag,tot_occ_rate

def get_polygon_from_2DLinestring(polygon):
	"""
	Extract polygon coordinates from 2D line string.
	"""
	poly_coords = polygon.split()
	poly_coords = numpy.array(poly_coords,dtype=float).reshape(len(poly_coords)/2,2)
	poly_coords = [[v1,v2] for v1,v2 in poly_coords]

	if poly_coords[0] != poly_coords[-1]:
		poly_coords.append(poly_coords[0])
	
	return poly_coords

def get_polygon_area(polygon):
	"""
	Compute polygon area in squared kilometers.
	"""
	lons = [lon for lon,lat in polygon]
	lats = [lat for lon,lat in polygon]
	
	west, east, north, south = _utils.get_spherical_bounding_box(lons, lats)
	proj = _utils.get_orthographic_projection(west, east, north, south)
	xx, yy = proj(lons, lats)
	
	polygon2d = shapely.geometry.Polygon(zip(xx, yy))
	
	return polygon2d.area

def parse_point_source(element):
	"""
	Parse NRML point source element, and extract:
	ID, name, point coordinates (as point), maximum magnitude (the maximum among all
	the maximum magnitudes from all the FMD defined),
	total occurrence rate (by summing occurrence rates from all the FMD defined)
	"""
	ID = element.get('%sid' % xmlGML)
	for e in element.iter():
		if e.tag == '%sname' % xmlGML:
			name = e.text
		if e.tag == '%spos' % xmlGML:
			point = numpy.array(e.text.split(),dtype=float)
		if e.tag == '%sruptureRateModel' % xmlNRML:
			max_mag, tot_occ_rate = parse_rupture_rate_model(e)

	return ID,name,point,None,max_mag,tot_occ_rate

def parse_simple_fault_source(element):
	"""
	Parse NRML simple fault source, and extract:
	ID, name, fault surface boundary (as polygon),
	maximum magnitude, total occurrence rate.
	"""
	ID = element.get('%sid' % xmlGML)
	for e in element.iter():
		if e.tag == '%sname' % xmlGML:
			name = e.text
		if e.tag == '%sposList' % xmlGML:
			posList = e.text
		if e.tag == '%sdip' % xmlNRML:
			dip = float(e.text)
		if e.tag == '%supperSeismogenicDepth' % xmlNRML:
			upper_seismo_depth = float(e.text)
		if e.tag == '%slowerSeismogenicDepth' % xmlNRML:
			lower_seismo_depth = float(e.text)
		if e.tag == '%struncatedGutenbergRichter' % xmlNRML:
			max_mag, tot_occ_rate = parse_truncated_gutenberg_richter(e)
		if e.tag == '%sevenlyDiscretizedIncrementalMFD' % xmlNRML:
			max_mag, tot_occ_rate = parse_incremental_mfd(e)

	polygon, area = get_polygon_area_from_simple_fault_data(posList,upper_seismo_depth,lower_seismo_depth,dip)

	# normalize total occurrence rate by area
	tot_occ_rate = tot_occ_rate / area

	return ID,name,None,polygon,max_mag,tot_occ_rate

def get_polygon_area_from_simple_fault_data(posList,upper_seismo_depth,lower_seismo_depth,dip):

	fault_top_edge = posList.split()
	fault_top_edge = numpy.array(fault_top_edge,dtype=float).reshape(len(fault_top_edge)/3,3)
	fault_top_edge = Line([Point(v1,v2,v3) for v1,v2,v3 in fault_top_edge])

	az = (fault_top_edge[0].azimuth(fault_top_edge[1]) + 270.0) % 360
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

def parse_complex_fault_source(element):
	"""
	Parse NRML complex fault source, and extract:
	ID, name, fault surface boundary (as polygon),
	maximum magnitude, total occurrence rate.
	"""
	ID = element.get('%sid' % xmlGML)
	for e in element.iter():
		if e.tag == '%sname' % xmlGML:
			name = e.text
		if e.tag == '%sfaultTopEdge' % xmlNRML:
			fault_top_edge = e.find('%sLineString' % xmlGML).findtext('%sposList' % xmlGML)
		if e.tag == '%sfaultBottomEdge' % xmlNRML:
			fault_bottom_edge = e.find('%sLineString' % xmlGML).findtext('%sposList' % xmlGML)
		if e.tag == '%struncatedGutenbergRichter' % xmlNRML:
			max_mag, tot_occ_rate = parse_truncated_gutenberg_richter(e)
		if e.tag == '%sevenlyDiscretizedIncrementalMFD' % xmlNRML:
			max_mag, tot_occ_rate = parse_incremental_mfd(e)

	polygon,area = get_polygon_area_from_complex_fault_data(fault_top_edge,fault_bottom_edge)

	tot_occ_rate = tot_occ_rate / area

	return ID,name,None,polygon,max_mag,tot_occ_rate

def get_polygon_area_from_complex_fault_data(fault_top_edge,fault_bottom_edge):
	
	fault_top_edge = fault_top_edge.split()
	fault_top_edge = numpy.array(fault_top_edge,dtype=float).reshape(len(fault_top_edge)/3,3)
	fault_top_edge = Line([Point(v1,v2,v3) for v1,v2,v3 in fault_top_edge])

	fault_bottom_edge = fault_bottom_edge.split()
	fault_bottom_edge = numpy.array(fault_bottom_edge,dtype=float).reshape(len(fault_bottom_edge)/3,3)
	fault_bottom_edge = Line([Point(v1,v2,v3) for v1,v2,v3 in fault_bottom_edge])

	# create complex fault surface
	surf = ComplexFaultSurface.from_fault_data([fault_top_edge,fault_bottom_edge], mesh_spacing=10)

	# extract fault boundary
	polygon = []
	surf_mesh = surf.get_mesh()
	fault_boundary = surf_mesh._get_bounding_mesh()
	for lon,lat in zip(fault_boundary.lons,fault_boundary.lats):
		polygon.append([lon,lat])

	# compute surface area
	_, _, _, cell_area = (surf_mesh.get_cell_dimensions())
	area = numpy.sum(cell_area)

	return polygon, area

def parse_rupture_rate_model(element):
	"""
	Parse NRML rupture rate model, and extract:
	- maximum magnitude (the maximum among all the maximum magnitudes from all the FMD defined),
	- total occurrence rate (by summing occurrence rates from all the FMD defined)
	"""
	max_mags = []
	tot_occ_rate = 0.0
	
	for e in element.iter():
		if e.tag == '%struncatedGutenbergRichter' % xmlNRML:
			max_mag, occ_rate = parse_truncated_gutenberg_richter(e)
		if e.tag == '%sevenlyDiscretizedIncrementalMFD' % xmlNRML:
			max_mag, occ_rate = parse_incremental_mfd(e)
		
	max_mags.append(max_mag)
	tot_occ_rate += occ_rate
	
	return max(max_mags),tot_occ_rate

def parse_truncated_gutenberg_richter(element):
	"""
	Parse NRML truncated GR element, and returns maximum magnitude
	and total occurrence rate.
	"""
	for e in element.iter():
		if e.tag == '%saValueCumulative' % xmlNRML:
			a_val = float(e.text)
		if e.tag == '%sbValue' % xmlNRML:
			b_val = float(e.text)
		if e.tag == '%sminMagnitude' % xmlNRML:
			min_mag = float(e.text)
		if e.tag == '%smaxMagnitude' % xmlNRML:
			max_mag = float(e.text)
	
	tot_occ_rate = pow(10.0,a_val - b_val * min_mag) - pow(10.0,a_val - b_val * max_mag)
	
	return max_mag, tot_occ_rate

def parse_incremental_mfd(element):
	"""
	Parse NRML evenly discretized incremental MFD, and returns
	maximum magnitude and total occurrence rate.
	"""
	rates = numpy.array(element.text.split(),dtype=float)
	max_mag = float(element.attrib['minVal']) + (len(rates) - 1) * float(element.attrib['binSize'])
	tot_occ_rate = numpy.sum(rates)
	
	return max_mag, tot_occ_rate

def serialize_data_to_shapefile(source_data,file_name):
	"""
	Serialize source model data to shapefile.
	"""
	for data in source_data:
		if data['POLYGON'] is not None:
			w_poly.poly(parts=[data['POLYGON']])
			w_poly.record(data['ID'],data['NAME'],data['MAX_MAG'],data['TOT_OCC_RATE'])
		if data['POINT'] is not None:
			w_point.point(data['POINT'][0],data['POINT'][1],0.0,0.0)
			w_point.record(data['ID'],data['NAME'],data['MAX_MAG'],data['TOT_OCC_RATE'])
	
	if len(w_poly.shapes()) > 0:
		w_poly.save(file_name)
	if len(w_point.shapes()) > 0:
		w_point.save(file_name)

	print 'Shapefile saved to: %s.shp' % file_name

def main(argv):
	"""
	Parse command line argument and performs requested action.
	"""
	parser = set_up_arg_parser()
	args = parser.parse_args()

	if args.source_model_file:
		source_data = parse_source_model_file(args.source_model_file)
		serialize_data_to_shapefile(source_data,args.source_model_file.split('.')[0])
	else:
		parser.print_help()

if __name__=='__main__':

	main(sys.argv)
