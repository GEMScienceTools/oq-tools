#!/usr/bin/python

"""
"""

import os
import re
import sys
import os.path
import numpy as np
from xml.dom import minidom
from optparse import OptionParser
from subprocess import call

TMP_FILE = "./tmp.tmp"

def get_coordinates_simple_fault_sources(xmldoc):
    coordinates_list = []
    fault_dat = xmldoc.getElementsByTagName('simpleFaultGeometry')
    for node in fault_dat:
        pos_list = node.getElementsByTagName('gml:posList')
        for pos in pos_list:
            coordinates = []
            for v in pos.firstChild.data.split():
                coordinates.append(float(v))
            coordinates_list.append(coordinates)
    return coordinates_list

def get_coordinates_area_sources(xmldoc):
    coordinates_list = []
    area_dat = xmldoc.getElementsByTagName('areaBoundary')
    for node in area_dat:
        pos_list = node.getElementsByTagName('gml:posList')
        for pos in pos_list:
            coordinates = []
            for v in pos.firstChild.data.split():
                coordinates.append(float(v))
            coordinates_list.append(coordinates)
    return coordinates_list

def create_ascii_file_area_sources(coordinates_list,file_name):
    ascii_file_name = file_name+"_area_sources.dat"
    ascii_file = open(ascii_file_name,'w')
    for i in range(0,len(coordinates_list)):
        aa = coordinates_list[i]
        ascii_file.write(">\n")
        for j in range(0,len(aa),2):
            ascii_file.write("%s %s\n" % (aa[j],aa[j+1]))
    ascii_file.write(">\n")
    ascii_file.close()
    if len(coordinates_list) == 0:
        ascii_file_name = None
    return ascii_file_name

def create_ascii_file_simple_fault_sources(coordinates_list,file_name):
    ascii_file_name = file_name+"_simple_fault_sources.dat"
    ascii_file = open(ascii_file_name,'w')
    for i in range(0,len(coordinates_list)):
        aa = coordinates_list[i]
        ascii_file.write(">\n")
        for j in range(0,len(aa),3):
            ascii_file.write("%s %s %s\n" % (aa[j],aa[j+1],aa[j+2]))
    ascii_file.write(">\n")
    ascii_file.close()
    if len(coordinates_list) == 0:
        ascii_file_name = None
    return ascii_file_name

def set_gmt_parameters():
    cmd = "gmtset MAP_FRAME_TYPE plain"; os.system(cmd) 
    cmd = "gmtset PS_MEDIA a4"; os.system(cmd)

    #cmd = "gmtset GRID_CROSS_SIZE_PRIMARY 0.2i"; os.system(cmd) 
    #cmd = "gmtset HEADER_FONT_SIZE        12p"; os.system(cmd)
    #cmd = "gmtset HEADER_FONT             22"; os.system(cmd)
    #cmd = "gmtset LABEL_FONT_SIZE         14p"; os.system(cmd)
    #cmd = "gmtset LABEL_FONT              22"; os.system(cmd)
    #cmd = "gmtset ANOT_FONT_SIZE  	      10p"; os.system(cmd)
    #cmd = "gmtset ANOT_FONT               21"; os.system(cmd)
    #cmd = "gmtset PS_IMAGE_FORMAT         hex"; os.system(cmd)

def create_gmt_plot(file_area_sources,file_simple_fault_sources,region_str,
        orientation_projection,output_file_name):
    postscript_file = output_file_name + ".eps"
    # Plotting
    cmd = "psbasemap " + region_str + " " + orientation_projection + \
            " -B5.0 -Xc -Yc -K > "+ postscript_file
    os.system(cmd) 
    cmd = "pscoast " + region_str + " " + orientation_projection + \
            " -Wthin -N1 -A1000 -Slightblue -O -K >> " + postscript_file
    os.system(cmd) 
    if file_area_sources is not None:
        cmd = "psxy " + file_area_sources + " " + region_str + " " + \
                orientation_projection + " -Wthick,blue  -O -K -L >> " \
                + postscript_file
        os.system(cmd) 
    if file_simple_fault_sources is not None:
        cmd = "psxy " + file_simple_fault_sources + " " + region_str + \
                " " + orientation_projection + " -Wthick,red -O -K >> " \
                + postscript_file
    os.system(cmd) 
    cmd = "pscoast " + region_str + " " + orientation_projection + \
            " -Wthin -N1 -A1000 -O >> " + postscript_file
    os.system(cmd) 

def get_min_max_lon_lat(xy_file_list):
    """
    Computes the min and max values of longitude and latitude
    """
    min_lon = +1e20
    max_lon = -1e20
    min_lat = +1e20
    max_lat = -1e20
    # Processing the xy files
    for file_xy in xy_file_list:
        if file_xy is not None:
            cmd = "minmax -C " + file_xy + " > " + TMP_FILE  
            os.system(cmd) 
            f = open(TMP_FILE,'r') 
            line = f.readline() 
            min_max_list = re.split("\s+",line)
            # Updating min and max values of longitude and latitude 
            min_lon = np.amin(np.array([min_lon,float(min_max_list[0])]))
            max_lon = np.amax(np.array([max_lon,float(min_max_list[1])]))
            min_lat = np.amin(np.array([min_lat,float(min_max_list[2])]))
            max_lat = np.amax(np.array([max_lat,float(min_max_list[3])]))
    # Create the region string 
    region_str = "-R%.2f/%.2f/%.2f/%.2f" % (min_lon, max_lon, min_lat, max_lat)
    return region_str, min_lon, max_lon, min_lat, max_lat

def main(argv):
    usage = "usage: python %prog [options]"
    epilog = "The usage of this script is conditional on the acceptance"+\
            "of the 'OATS Terms and Conditions of Use', available at the "+\
            "following address http://openquake.org/alpha-testing-services/"
    description = "Script for plotting seismic source geometries " +\
			"in a nrml file. It produces a map in postscript file " +\
            "using GMT (http://gmt.soest.hawaii.edu)"
    parser = OptionParser(usage=usage,
            version="%prog 0.1 - 2012.04.23",
            epilog=epilog,
            description=description)
    parser.add_option("-i", "--source_model", 
   		    dest="file_name_seismic_source_model",
			default=None,
            help="parses and plots information in a nrml formatted FILE", 
            metavar="FILE")
    parser.add_option("-r", "--region", 
   		    dest="map_region",
			default=None,
            help="sets map extension [e.g. -r minLon/minLat/maxLon/maxLat]", 
            )
    parser.add_option("-p", "--portrait", 
   		    dest="map_orientation",
			action="store_true",
            help="sets map portrait orientation [default is landscape]", 
            )
    parser.add_option("-o", "--output_file", 
   		    dest="output_file_name",
			default="map",
            help="sets the output file name", 
            metavar="FILE")
    # Parse command line arguments
    (options, args) = parser.parse_args()
    # Fix orientation and projection page width
    output_file_name = options.output_file_name
    # Parse nrml file
    xmldoc = minidom.parse(options.file_name_seismic_source_model)
    # Retrieving files
    file_area_sources = create_ascii_file_area_sources(
            get_coordinates_area_sources(xmldoc),output_file_name)
    file_simple_fault_sources = create_ascii_file_simple_fault_sources(
            get_coordinates_simple_fault_sources(xmldoc),output_file_name)

    if options.map_region:
        region_str = "-R"+options.map_region
    else:
         min_max_str = get_min_max_lon_lat([
                file_area_sources, file_simple_fault_sources])
         print "min lon: %.2f max lon: %.2f" % (min_max_str[1],min_max_str[2])
         print "min lat: %.2f max lat: %.2f" % (min_max_str[3],min_max_str[4])
         region_str = min_max_str[0] 
    # Fix orientation and projection page width
    if options.map_orientation:
        orientation_projection = "-P -JM13c"
    else:
	    orientation_projection = "-JM20c"
    # Set GMT default parameters
    set_gmt_parameters()
    # Creating the GMT plot
    create_gmt_plot(file_area_sources,
            file_simple_fault_sources,
            region_str,
            orientation_projection,
            output_file_name)
    # Remove temporary files
    if os.path.exists(TMP_FILE):
        call(["rm",TMP_FILE])
    if os.path.exists("gmt.conf"):
        call(["rm","gmt.conf"])

if __name__=='__main__':

    if len(sys.argv) == 1:
        sys.argv.append('--help')   
    
    main(sys.argv)
    print "done"
