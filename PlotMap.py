import os
import re
import math
os.system("gmtset GRID_CROSS_SIZE_PRIMARY = 0.2i") 
os.system("gmtset BASEMAP_TYPE            = PLAIN") 
os.system("gmtset HEADER_FONT_SIZE        = 12p")
os.system("gmtset PAPER_MEDIA             = a4+")
os.system("gmtset HEADER_FONT             = 22")
os.system("gmtset LABEL_FONT_SIZE         = 14p")
os.system("gmtset LABEL_FONT              = 22")
os.system("gmtset ANOT_FONT_SIZE  	      = 10p")
os.system("gmtset ANOT_FONT               = 21")
os.system("gmtset PS_IMAGE_FORMAT         = hex")
idir = "./dat/"

# INPUTFILE
fleMap = idir+"popMessinaCity.txt";
tmp = "./tmp/tmp.tmp"

cmd = "minmax -m -C " + fleMap + " > " + tmp   
os.system(cmd) 
f = open(tmp,'r'); line = f.readline(); aa = re.split("\s+",line)

# DEFINE THE EXTENSION
# Currently this script reads all the values of the input file and sets automatically the extend of the map based on the minimum and maximum values. Different regions can be selected, by defining these values manually. 
ext = "%.2f/%.2f/%.2f/%.2f" % \
	(float(aa[0]),float(aa[1]),float(aa[2]),float(aa[3]))

# PLOTTING
cmd = "pscoast -R"+ext+" -X6.0c -JM15 -Df -Na -G230 -V -K > tmp.eps" 
os.system(cmd)
	
# CREATE GRID 
awkcmd = "gawk '{print $1, $2, $3}' " + fleMap
os.system(awkcmd)
	
# CREATE CPT
# The cpt file dictates the color palette that is going to applied in the map. Different cpt files can be downloaded from online databases (e.g.: cpt-city) and used on the maps. Users can also create their own cpt-files by modifying the existing cpt-files in located in the cpt folder. cptfile = "./cpt/ad-a.cpt"; 
cptf = "./cpt/Blues_08.cpt"
cmd = "makecpt -C"+cptfile+" -T0/11/1 -Q -D255/255/255 > "+cptf
os.system(cmd)

# PLOT MAP
cmd = "gawk '{print $1, $2, $3}' "+fleMap+" | psxy -JM -O -K -R"+ext+" -C"+cptf+" -Ss0.5  >> tmp.eps"
os.system(cmd)

# CREATE THE SCALE AND LEGEND
# This lines serves to define the position and size of the scale, as well as the respective legend text.
cmd = "psscale -D7.5/-1/15c/0.3ch -N1 -O -K -Q -C"+cptf+" -B::/::>> tmp.eps"
os.system(cmd)

cmd = "pscoast -R"+ext+" "+" -JM -W -Df -Na -V -B0.25/0.25/25 -O -Slightblue >> tmp.eps" 
os.system(cmd)