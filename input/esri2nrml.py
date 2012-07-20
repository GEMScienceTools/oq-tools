# Copyright (c) 2010-2012, GEM Foundation.
#
# esri2nrml is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# esri2nrml is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with esri2nrml. If not, see <http://www.gnu.org/licenses/>.

"""
Simple LandScan ESRI binary file to NRML converter
for exposure population models. 
"""

import struct
import ConfigParser
import argparse
import sys
import math
import datetime
from lxml import etree


NRML_NS = "http://openquake.org/xmlns/nrml/0.3"
GML_NS = "http://www.opengis.net/gml"
NSMAP = {None: NRML_NS, "gml": GML_NS}
NRML = "{%s}" % NRML_NS
GML = "{%s}" % GML_NS


def read_binary_data(filename):
    results = []

    with open(filename, "rb") as data:
        # at the moment, we only support two bytes
        # integer format.
        bytes_read = data.read(2)
        while bytes_read:
            # at the moment, we only support LSB format.
            results.append(struct.unpack("<h", bytes_read)[0])
            bytes_read = data.read(2)

    return results


def read_metadata(filename):
    config = ConfigParser.ConfigParser()
    config.read(filename)

    return config


def cmd_parser():
    args_parser = argparse.ArgumentParser(prog="esri2nrml",
        usage="%(prog)s [options]")
    
    args_parser.add_argument("-d", "--data",
        dest="data", nargs="?", required=True,
        help="file containing the binary data (binary ESRI)")

    args_parser.add_argument("-m", "--mdata",
        dest="mdata", nargs="?", required=True,
        help="file containing the metadata (.ini)")

    args_parser.add_argument("-t", "--taxonomy",
        dest="taxonomy", nargs="?", required=True,
        help="assets taxonomy")

    return args_parser


def asset_iterator(config, data):
    nrows = config.getint("georeference", "nrows")
    ncols = config.getint("georeference", "ncols")

    xmin = config.getfloat("georeference", "xmin")
    ymin = config.getfloat("georeference", "ymin")
    xmax = config.getfloat("georeference", "xmax") 
    ymax = config.getfloat("georeference", "ymax") 

    x_step = math.fabs((xmax - xmin) / ncols)
    y_step = math.fabs((ymax - ymin) / nrows)

    assert nrows * ncols == len(data)

    current_x = xmin
    current_y = ymax

    for counter, value in enumerate(data, start=1):
        assert xmin <= current_x <= xmax
        assert ymin <= current_y <= ymax
        
        yield (current_x, current_y, value)
        
        current_x = current_x + x_step

        # we are on the last column.
        if counter % ncols == 0:
            current_x = xmin
            current_y = current_y - y_step


class ExposureModelWriter(object):

    def __init__(self, taxonomy):
        self.counter = 1
        self.taxonomy = taxonomy
        
        # <nrml /> element
        self.root = etree.Element("nrml", nsmap=NSMAP)
        self.root.set("%sid" % GML, "n1")

        exp_model = etree.SubElement(self.root, "exposureModel")
        exp_model.set("%sid" % GML, "em1")

        etree.SubElement(exp_model, "config")

        # <exposureList /> element
        self.exposure_list = etree.SubElement(exp_model, "exposureList")
        self.exposure_list.set("%sid" % GML, "el1")
        self.exposure_list.set("assetCategory", "population")

        etree.SubElement(self.exposure_list, "%sdescription" % GML)
        etree.SubElement(self.exposure_list, "taxonomySource")

    def add(self, asset_data):
        asset = etree.SubElement(self.exposure_list, "assetDefinition")
        asset.set("%sid" % GML, "asset_" + str(self.counter))

        site = etree.SubElement(asset, "site")
        point = etree.SubElement(site, "%sPoint" % GML)
        point.set("srsName", "epsg:4326")
        pos = etree.SubElement(point, "%spos" % GML)
        pos.text = " ".join([str(asset_data[0]), str(asset_data[1])])

        number = etree.SubElement(asset, "number")
        number.text = str(asset_data[2] if asset_data[2] >= 0 else 0)

        taxonomy = etree.SubElement(asset, "taxonomy")
        taxonomy.text = self.taxonomy

        self.counter += 1

    def serialize(self):
        with open("exp_model.xml", "w") as fh:

            fh.write(etree.tostring(
                    self.root, pretty_print=True,
                    xml_declaration=True,
                    encoding="UTF-8"))


if __name__ == "__main__":
    parser = cmd_parser()
    args = None

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)
    else:
        args = parser.parse_args()
    
    started_at = datetime.datetime.now()
    print ">> Started at: " + str(started_at)

    metadata = read_metadata(args.mdata)
    bdata = read_binary_data(args.data)

    writer = ExposureModelWriter(args.taxonomy)

    for asset_data in asset_iterator(metadata, bdata):
        writer.add(asset_data)

    writer.serialize()

    elapsed_time = (datetime.datetime.now() - started_at)
    print ">> Time spent: %ss, %sms" % (
        str(elapsed_time.seconds), str(
        elapsed_time.microseconds / 1000))
