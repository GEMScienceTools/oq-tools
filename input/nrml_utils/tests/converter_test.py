# Copyright (c) 2010-2012, GEM Foundation.
#
# NRML is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NRML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with NRML.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
from lxml import etree
from StringIO import StringIO

from nrml_utils.reader import ExposureTxtReader
from nrml_utils.writer import ExposureWriter

NRML_SCHEMA_FILE = os.path.abspath('../nrml_utils/schema/nrml.xsd')

def validates_against_xml_schema(xml_filename, xml_schema_path):
    xml_doc = etree.parse(xml_filename)
    xmlschema = etree.XMLSchema(etree.parse(xml_schema_path))
    return xmlschema.validate(xml_doc)


class AnExposureTxtReaderShould(unittest.TestCase):

    def setUp(self):
        self.content = StringIO('expModId,assetCategory,description,stcoType,'
                                'stcoUnit,areaType,areaUnit,cocoType,'
                                'cocoUnit,recoType,recoUnit,taxonomySource\n'
                                'PAV01,buildings,Collection of existing '
                                'building in downtown Pavia,aggregated,USD,'
                                'per_asset,GBP,per_area,CHF,aggregated, '
                                'EUR,pavia taxonomy\n\n'
                                'lon,lat,taxonomy,stco,number,area,reco,coco,'
                                'occupantDay,occupantNight,deductible,limit\n'
                                '28.6925,40.9775,RC_MR_LC,40000,50,1500,4000,'
                                '1000,10,,0.05,32000\n'
                                '28.6975,40.9825,RC_MR_LC,300000,100,1000,'
                                '30000,2000,15,,0.10,240000')
        self.exp_reader = ExposureTxtReader(self.content)

    def test_read_meta_data(self):
        desc = 'Collection of existing building in downtown Pavia'
        expected_meta_data = dict(
            expModId='PAV01', assetCategory='buildings', description=desc,
            stcoType='aggregated', stcoUnit='USD', areaType='per_asset',
            areaUnit='GBP', cocoType='per_area', cocoUnit='CHF',
            recoType='aggregated', recoUnit='EUR',
            taxonomySource='pavia taxonomy')

        self.assertEqual(expected_meta_data, self.exp_reader.metadata)

    def test_read_assets(self):
        first_asset = {'reco': '4000', 'area': '1500', 'taxonomy': 'RC_MR_LC',
                       'stco': '40000', 'lon': '28.6925', 'number': '50',
                       'coco': '1000', 'limit': '32000', 'lat': '40.9775',
                       'occupantNight': '', 'occupantDay': '10',
                       'deductible': '0.05'}
        second_asset = {'reco': '30000', 'area': '1000', 'taxonomy': 'RC_MR_LC',
                        'stco': '300000', 'lon': '28.6975', 'number': '100',
                        'coco': '2000', 'limit': '240000', 'lat': '40.9825',
                        'occupantNight': '', 'occupantDay': '15',
                        'deductible': '0.10'}

        expected_assets = [first_asset, second_asset]
        self.assertEqual(expected_assets, self.exp_reader.readassets())


class AnExposureWriterShould(unittest.TestCase):

    def setUp(self):
        self.output_filename = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'data/pippo.xml'))

        desc = 'Collection of existing building in downtown Pavia'
        self.metadata = dict(
            expModId='PAV01', assetCategory='buildings', description=desc,
            stcoType='aggregated', stcoUnit='USD', areaType='per_asset',
            areaUnit='GBP', cocoType='per_area', cocoUnit='CHF',
            recoType='aggregated', recoUnit='EUR',
            taxonomySource='pavia taxonomy')

        self.first_asset = {'reco': '4000', 'area': '1500',
                         'taxonomy': 'RC_MR_LC',
                       'stco': '40000', 'lon': '28.6925', 'number': '50',
                       'coco': '1000', 'limit': '32000', 'lat': '40.9775',
                       'occupantNight': '', 'occupantDay': '10',
                       'deductible': '0.05'}

        self.second_asset = {'reco': '30000', 'area': '1000',
                         'taxonomy': 'RC_MR_LC',
                        'stco': '300000', 'lon': '28.6975', 'number': '100',
                        'coco': '2000', 'limit': '240000', 'lat': '40.9825',
                        'occupantNight': '', 'occupantDay': '15',
                        'deductible': '0.10'}
        self.third_asset = {'reco': '', 'area': '',
                            'taxonomy': 'RC_MR_LC',
                            'stco': '', 'lon': '28.6975', 'number': '',
                            'coco': '', 'limit': '', 'lat': '40.9825',
                            'occupantNight': '', 'occupantDay': '',
                            'deductible': ''}

        self.writer = ExposureWriter()

    def test_serialize(self):
        self.writer.serialize(self.output_filename, self.metadata,
            [self.first_asset, self.second_asset, self.third_asset])

        self.assertTrue(validates_against_xml_schema(self.output_filename,
            NRML_SCHEMA_FILE))

