#!/usr/bin/python

"""
Plot disaggregation results stored in a hdf5 file as produced by OpenQuake using GMT (http://gmt.soest.hawaii.edu/).
Requires argparse, h5py, numpy, and GMT.
GMT must be defined in the PATH.

Example:

./plotDisaggregation.py --config_file=config.gem --results_file=results.h5
"""

import sys
import ConfigParser
import argparse
import h5py
import numpy
from subprocess import call

# predefined colors for plotting 3rd dimension data
COLORS = ['blue','green','red','cyan','magenta','yellow','black','white']

# tectonic region types
TECT_REGS = ['ACTIVE', 'STABLE', 'SUB_INTER', 'SUB_INTRA', 'VOLCANIC']

# list of pmfs that can be plotted
SUPPORTED_PMFS = ['TRTPMF','MagDistEpsPMF','DistPMF','MagPMF','MagDistPMF','LatLonPMF']

def set_up_arg_parser():
	"""
	Set up command line parser.
	"""
	parser = argparse.ArgumentParser(description='Plot disaggregation results stored'\
		' in a hdf5 file as produced by OpenQuake using GMT.')
	parser.add_argument('--config_file',help='path to OpenQuake configuration file'\
		' used for generating disaggregation results.')
	parser.add_argument('--results_file',help='path to hdf5 file containing disaggregation results')
	parser.add_argument('--xy_size',help='plot size along x and y (in cm)',default=15)
	parser.add_argument('--z_size',help='plot size along z (in cm)',default=10)
	return parser
	
def get_bin_limits(file_name):
	"""
	Parse OpenQuake configuration file
	and returns disaggregation bin limits.
	"""
	config = ConfigParser.ConfigParser()
	config.readfp(open(file_name))
	
	longitude_bin_limits = config.get('HAZARD','LONGITUDE_BIN_LIMITS').split(',')
	latitude_bin_limits = config.get('HAZARD','LATITUDE_BIN_LIMITS').split(',')
	mag_bin_limits = config.get('HAZARD','MAGNITUDE_BIN_LIMITS').split(',')
	epsilon_bin_limits = config.get('HAZARD','EPSILON_BIN_LIMITS').split(',')
	distance_bin_limits = config.get('HAZARD','DISTANCE_BIN_LIMITS').split(',')
	
	return {'lons':longitude_bin_limits,\
			'lats':latitude_bin_limits,\
			'mags':mag_bin_limits,\
			'eps':epsilon_bin_limits,\
			'dists':distance_bin_limits}
	
def create_xyz_file(x,y,z,file_name):
	"""
	Write x,y,z data to ASCII file.
	"""
	xyz_file = open(file_name,'w')
	
	if len(x) != len(y) or len(x) != len(z) or len(y) != len(z):
		raise ValueError('x,y,z data are not consistent')
	
	for i in range(len(x)):
		xyz_file.write("%s %s %s\n" % (x[i],y[i],z[i]))
	xyz_file.close()
	
def create_xy_file(x,y,file_name):
	"""
	Write x,y data to ASCII file.
	"""
	xy_file = open(file_name,'w')
	
	if len(x) != len(y):
		raise ValueError('x and y data are not consistent')
		
	for i in range(len(x)):
		xy_file.write("%s %s\n" % (x[i],y[i]))
	xy_file.close()
	
def create_legend_file(dim,file_name,header):
	"""
	Write legend file for GMT pslegend.
	Return legend size (hight and width)
	"""
	legend_file = open(file_name,'w')
	
	legend_file.write("H 18 Times-Roman %s\n" % (header))
	for i in range(len(dim) - 1):
		legend_file.write("G 1.0c\n")
		legend_file.write("S 1.0c s 1.0c %s 0.25p 2.0c %s - %s\n" % (COLORS[i],dim[i],dim[i+1]))
	legend_file.close()
	
	hight = (len(dim) - 1) * 2 + 1
	width = 4.0
	
	return hight,width

def plot_lat_lon_pmf(pmf,lat,lon,args):
	"""
	Plot latitude longitude PMF
	"""
	region = "-R%s/%s/%s/%s/%s/%s" % (lon[0], lon[-1],lat[0], lat[-1],0.0,numpy.max(pmf))
	projection = "-JM%s/%s/%s" % (lon[0],lat[0],args.xy_size)
	annotation = '-B:Longitude:%s/:Latitude:%s/%s:Probability::.%s:WeSnZ' % \
		(0.5,0.5,0.1,"Longitude-Latitude PMF")

	call(["gmtset",'PLOT_DEGREE_FORMAT','ddd:mmF'])
	
	# plot bars one by one
	plot_file = open("lat_lon_pmf.ps",'w')
	call(["pscoast",region,projection,annotation,'-Z0','-JZ8c','-E200/30',
		'-Gblack','-K'],stdout=plot_file)
	for i in range(len(lat) - 2,-1,-1):
		for j in range(len(lon) - 2,-1,-1):

			x = [(lon[j] + lon[j+1]) / 2]
			y = [(lat[i] + lat[i+1]) / 2]
			z = [pmf[i,j]]

			create_xyz_file(x,y,z,'hist.dat')

			if i == len(lon) - 2 and j==len(lat) - 2:
				call(["psxyz","hist.dat",region,projection,
						'-JZ8c','-E200/30','-So0.5b','-Wthinnest',
						'-Ggray','-K','-O'],stdout=plot_file)
			else:
				call(["psxyz","hist.dat",region,projection,
						'-JZ8c','-E200/30','-So0.5b','-Wthinnest',
						'-Ggray','-O','-K'],stdout=plot_file)

			call(["rm","hist.dat"])

def plot_mag_dist_pmf(pmf,mag,dist,args):
	"""
	Plot magnitude-distance pmf.
	"""
	region = "-R%s/%s/%s/%s/%s/%s" % (mag[0], mag[-1],dist[0], dist[-1],0.0,numpy.max(pmf))
	projection = "-JX%sc/%sc" % (args.xy_size,args.xy_size)
	annotation = '-B:Magnitude (Mw):%s/:Distance (km):%s/%s:Probability::.%s:WeSnZ' % \
		(0.5,5.0,0.1,"Magnitude-Distance PMF")
	
	# plot bars one by one
	plot_file = open("mag_dist_pmf.ps",'w')
	for i in range(len(mag) - 2,-1,-1):
		for j in range(len(dist) - 2,-1,-1):

			x = [(mag[i] + mag[i+1]) / 2]
			y = [(dist[j] + dist[j+1]) / 2]
			z = [pmf[i,j]]

			create_xyz_file(x,y,z,'hist.dat')

			if i == len(mag) - 2 and j==len(dist) - 2:
				call(["psxyz","hist.dat",region,projection,
						'-JZ8c',annotation,'-E200/30','-So0.5','-Wthinnest','-Ggray','-K'],stdout=plot_file)
			else:
				call(["psxyz","hist.dat",region,projection,
						'-JZ8c','-E200/30','-So0.5b','-Wthinnest','-Ggray','-O','-K'],stdout=plot_file)

			call(["rm","hist.dat"])
	plot_file.close()
	
def plot_mag_dist_eps_pmf(pmf,mag,dist,eps,args):
	"""
	Plot magnitude-distance-epsilon pmf.
	"""
	region = "-R%s/%s/%s/%s/%s/%s" % (mag[0], mag[-1],dist[0], dist[-1],0.0,numpy.max(pmf))
	projection = "-JX%sc/%sc" % (args.xy_size,args.xy_size)
	annotation = '-B:Magnitude (Mw):%s/:Distance (km):%s/%s:Probability::.%s:WeSnZ' % \
	 (0.5,5.0,0.02,"Magnitude-Distance-Epsilon PMF")
	
	# plot bars one by one
	plot_file = open("mag_dist_eps_pmf.ps",'w')
	for i in range(len(mag) - 2,-1,-1):
		for j in range(len(dist) - 2,-1,-1):
			
			# sort values from minimum to maximum
			values = numpy.sort(pmf[i,j,:])
			for k,v in enumerate(values):
				
				color_index = numpy.where(pmf[i,j,:]==v)
				color = COLORS[color_index[0][0]]
				
				x = [(mag[i] + mag[i+1]) / 2]
				y = [(dist[j] + dist[j+1]) / 2]
				if k == 0:
					base_hight = 0.0
				else:
					base_hight = values[k-1]
				z = [v]
				create_xyz_file(x,y,z,'hist.dat')
				
				if i == len(mag) - 2 and j==len(dist) - 2 and k == 0:
					call(["psxyz","hist.dat",region,projection,'-JZ8c',
						annotation,'-E200/30','-So0.5','-Wthinnest','-G'+color,'-K'],stdout=plot_file)
				else:
					call(["psxyz","hist.dat",region,projection,'-JZ8c',
						'-E200/30','-So0.5b'+str(base_hight),'-Wthinnest','-G'+color,
						'-O','-K'],stdout=plot_file)
				
				call(["rm","hist.dat"])
				
	# plot legend
	hight,width = create_legend_file(eps,"legend.dat","Epsilon")
	legend_postion = "-Dx%sc/%sc/%sc/%sc/BL" % \
					(float(args.xy_size) + width / 2, float(args.z_size) - hight / 2, width, hight)
	call(["pslegend","legend.dat","-R","-J",legend_postion,"-O"],stdout=plot_file)
	call(["rm","legend.dat"])
	
def plot_trt_pmf(pmf,args):
	"""
	Plot tectonic region type pmf.
	"""
	region = "-R0/5/%s/%s" % (0,numpy.max(pmf))
	projection = "-JX%s/%s" % (args.xy_size,args.z_size)
	annotation = "-B:Tectonic Region Type:/:Probability:%s:.Tectonic Region Type PMF:WS" % (0.1)
	
	plot_file = open("trt_pmf.ps",'w')
	create_xy_file(range(1,6),pmf,"hist.dat")
	call(["psxy","hist.dat",region,projection,annotation,"-Ggray","-Xc","-Yc","-Sb0.5",
		"-K"],stdout=plot_file)
	call(["rm","hist.dat"])
	
	annotation_file = open("annotation.dat",'w')
	for i in range(len(TECT_REGS)):
		annotation_file.write("%s %s %s %s %s %s %s\n" % (i+1-0.3,-0.05,10,0.0,0,0.1,TECT_REGS[i]))
	annotation_file.close()
	call(["pstext","annotation.dat","-R","-J","-N","-O","-K"],stdout=plot_file)
	call(["rm","annotation.dat"])

def plot_dist_pmf(pmf,dists,args):
	"""
	Plot distance pmf.
	"""
	region = "-R0/%s/%s/%s" % (dists[-1],0,numpy.max(pmf))
	projection = "-JX%s/%s" % (args.xy_size,args.z_size)
	annotation = "-B:Distance:%s/:Probability:%s:.Distance PMF:WS" % (5.0,0.1)

	# compute distance bin centers from distance bin edges
	d = []
	for i in range(len(dists) - 1):
		d.append((dists[i] + dists[i+1]) / 2.0)

	plot_file = open("dist_pmf.ps",'w')
	create_xy_file(d,pmf,"hist.dat")
	call(["psxy","hist.dat",region,projection,annotation,"-Ggray","-Xc","-Yc","-Sb0.5"],stdout=plot_file)
	call(["rm","hist.dat"])

def plot_mag_pmf(pmf,mags,args):
	"""
	Plot distance pmf.
	"""
	region = "-R%s/%s/%s/%s" % (mags[0],mags[-1],0,numpy.max(pmf))
	projection = "-JX%s/%s" % (args.xy_size,args.z_size)
	annotation = "-B:Magnitude:%s/:Probability:%s:.Distance PMF:WS" % (1.0,0.1)

	# compute magnitude bin centers from magnitude bin edges
	m = []
	for i in range(len(mags) - 1):
		m.append((mags[i] + mags[i+1]) / 2.0)

	plot_file = open("mags_pmf.ps",'w')
	create_xy_file(m,pmf,"hist.dat")
	call(["psxy","hist.dat",region,projection,annotation,"-Ggray","-Xc","-Yc","-Sb0.5"],stdout=plot_file)
	call(["rm","hist.dat"])

def main(argv):
	
	parser = set_up_arg_parser()
	args = parser.parse_args()
	
	if args.config_file and args.results_file:
		
		# extract bin limits and disaggregation results
		bin_limits = get_bin_limits(args.config_file)
		diss_data = h5py.File(args.results_file,'r')
		
		# loop over disaggregation results and plot the
		# pmfs that are currently supported
		pmfs =  diss_data.keys()
		for pmf_key in pmfs:
			
			if pmf_key in SUPPORTED_PMFS:
				print 'plotting %s...'% (pmf_key)
				
				if pmf_key == 'MagDistEpsPMF':
					plot_mag_dist_eps_pmf(diss_data.get(pmf_key),\
						numpy.array(bin_limits['mags'],dtype=float),\
						numpy.array(bin_limits['dists'],dtype=float),\
						numpy.array(bin_limits['eps'],dtype=float), \
						args)
											
				if pmf_key == 'TRTPMF':
					plot_trt_pmf(diss_data.get(pmf_key),args)

				if pmf_key == 'DistPMF':
					plot_dist_pmf(diss_data.get(pmf_key),numpy.array(bin_limits['dists'],dtype=float),args)

				if pmf_key == 'MagPMF':
					plot_mag_pmf(diss_data.get(pmf_key),numpy.array(bin_limits['mags'],dtype=float),args)

				if pmf_key == 'MagDistPMF':
					plot_mag_dist_pmf(diss_data.get(pmf_key),
								numpy.array(bin_limits['mags'],dtype=float),
								numpy.array(bin_limits['dists'],dtype=float),args)

				if pmf_key == 'LatLonPMF':
					plot_lat_lon_pmf(diss_data.get(pmf_key),
								numpy.array(bin_limits['lats'],dtype=float),
								numpy.array(bin_limits['lons'],dtype=float),args)

				print 'done.'
			else:
				print '%s not supported for plotting, sorry.' % (pmf_key)
				continue
	else:
		parser.print_help()
		
if __name__=='__main__':
	
	main(sys.argv)
	
