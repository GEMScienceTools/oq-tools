# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010-2011, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with OpenQuake. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
map_creator creates map in eps format
taking loss_map input file. The generated
output is in ./computed_output
"""

import argparse
from collections import namedtuple
from lxml import etree
import os
import sys

from plotmap import create_map

MSG_ERROR_NO_OUTPUT_FILE = 'Error: unspecified output file\n'
MSG_ERROR_NONEXISTENT_FILE = 'Error: nonexistent input file\n'
OUTPUT_DIR = 'computed_output'
OUTPUT_DAT = 'dat'

NRML_NS = '{http://openquake.org/xmlns/nrml/0.3}'

LM_NODE = '%sLMNode' % NRML_NS

POS_NODE = '{http://www.opengis.net/gml}pos'

LOSS_NODE_ELEM = '%sloss' % NRML_NS

MEAN_NODE = '%smean' % NRML_NS

ENTRY = namedtuple('Entry', 'lon, lat, sum_mean')


def build_cmd_parser():
    """Create a parser for cmdline arguments"""

    parser = argparse.ArgumentParser(prog='MapCreator')

    parser.add_argument('-i', '--input-file',
                        nargs=1,
                        metavar='input file',
                        dest='input_file',
                        help='Specify the input file (i.e. loss_map.xml)')

    parser.add_argument('-r', '--res',
                        nargs=1,
                        default=[0.5],
                        type=float,
                        help='resolution of each dot',
                        metavar='value',
                        dest='res')

    parser.add_argument('-min', "--min-val",
                        nargs=1,
                        default=[100.0],
                        type=float,
                        help='minimum value in a loss map',
                        metavar='value',
                        dest='min_val')

    parser.add_argument('-max', '--max-val',
                        nargs=1,
                        default=[1000000000.0],
                        type=float,
                        help='maximum value in a loss map',
                        metavar='value',
                        dest='max_val')

    parser.add_argument('-v', '--version',
                        action='version',
                        version="%(prog)s 0.0.1")

    return parser


def create_output_folders():
    """
    Create, if absent computed_output/
    and computed_output/dat folders
    inside main dir
    """

    output_dir = os.path.join(OUTPUT_DIR, OUTPUT_DAT)
    no_folder = not os.path.exists(output_dir)
    if no_folder:
        os.makedirs(output_dir)


def compute_map(loss_map_file_name, args):
    output_file_name = os.path.basename(loss_map_file_name)[0:-4] + '.txt'
    compute_map_output = os.path.join(OUTPUT_DIR, OUTPUT_DAT, output_file_name)
    write_loss_map_entries(compute_map_output,
            read_loss_map_entries(loss_map_file_name))
    create_map(OUTPUT_DIR, compute_map_output,
            args.res[0], args.min_val[0],
            args.max_val[0])


def read_loss_map_entries(loss_map_xml):
    """Create loss maps entries by parsing a loss map file"""

    entries = []

    elem = 1

    with open(loss_map_xml) as loss_file:
        for node in etree.iterparse(loss_file):
            if node[elem].tag == LM_NODE:
                lon, lat = node[elem].find('.//%s' % POS_NODE).text.split()

                loss_nodes = node[elem].findall('.//%s' % LOSS_NODE_ELEM)

                sum_mean = 0
                for loss_node in loss_nodes:
                    sum_mean += float(loss_node.find('.//%s' % MEAN_NODE).text)

                entries.append(ENTRY(lon, lat, sum_mean))
                node[elem].clear()

    return entries


def write_loss_map_entries(output_filename, loss_entries):
    """
    Write loss map entries to txt file
    where every entry is in the form
    longitude, latitude, sum_mean
    """

    with open(output_filename, 'w') as out_file:
        out_file.write('x,y,value\n')
        for entry in loss_entries:
            entry_string = ','.join(
                [entry.lon, entry.lat, str(entry.sum_mean)]) + '\n'
            out_file.write(entry_string)


def main():

    parser = build_cmd_parser()
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if args.input_file != None:
            if os.path.exists(args.input_file[0]):
                create_output_folders()
                compute_map(args.input_file[0], args)
            else:
                print MSG_ERROR_NONEXISTENT_FILE
                parser.print_help()

if __name__ == '__main__':
    main()
