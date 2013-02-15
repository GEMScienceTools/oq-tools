The mapcreator script allows to create maps using gmt_,
by giving a loss map as input. It depends on gmt, its
coast lines and gawk.

Install gmt::

    $ sudo apt-get install gmt gawk

Download gmt coastlines (use 7 in the mirror site selection)::

    $ gmt-coastline-download

Update PATH env variable, with gmt's bin dir::

    $ export PATH=$PATH:/usr/lib/gmt/bin

Usage:: 

    $ python map_creator.py -i loss-map.xml

Usage with optional arguments ::

    $ python map_creator.py -i loss-map.xml -r 0.6 -min 150 -max 1000000

Default values for optional arguments are:

- *-r or --res* resolution 0.5
- *-min or --min-val* minimum value 100.0
- *-max or --max-val* maximum value 1000000000.0

.. _gmt: http://gmt.soest.hawaii.edu/
