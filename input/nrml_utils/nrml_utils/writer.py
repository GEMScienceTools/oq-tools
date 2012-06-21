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

from lxml import etree

NRML_NS = 'http://openquake.org/xmlns/nrml/0.3'
GML_NS = 'http://www.opengis.net/gml'
NRML = "{%s}" % NRML_NS
GML = "{%s}" % GML_NS
NSMAP = {None: NRML_NS, "gml": GML_NS}

ROOT = "%snrml" % NRML
GML_ID = "%sid" % GML
EXPOSURE_MODEL = "%sexposureModel" % NRML
CONFIG = "%sconfig" % NRML
EXPOSURE_LIST = "%sexposureList" % NRML

# Exposure List attributes names
AREA_TYPE = 'areaType'
AREA_UNIT = 'areaUnit'
ASSET_CATEGORY = 'assetCategory'
COCO_TYPE = 'cocoType'
COCO_UNIT = 'cocoUnit'
RECO_TYPE = 'recoType'
RECO_UNIT = 'recoUnit'
STCO_TYPE = 'stcoType'
STCO_UNIT = 'stcoUnit'

DESCRIPTION =  '%sdescription' % GML
TAXONOMY_SOURCE = '%staxonomySource' % NRML

# Asset definition tagnames
ASSET = "%sassetDefinition" % NRML
SITE = "%ssite" % NRML
GML_POINT = "%sPoint" % GML
GML_SRS_ATTR_NAME = 'srsName'
GML_SRS_EPSG_4326 = 'epsg:4326'
GML_POS = "%spos" % GML
AREA = '%sarea' % NRML
COCO = '%scoco' % NRML
DEDUCTIBLE = '%sdeductible' % NRML
LIMIT = '%slimit' % NRML
NUMBER = '%snumber' % NRML
OCCUPANTS = '%soccupants' % NRML
RECO = '%sreco' % NRML
STCO = '%sstco' % NRML
TAXONOMY = '%staxonomy' % NRML

NO_VALUE = ''


class ExposureWriter(object):

    def serialize(self, filename, metadata, assets):
        root_elem = self._write_header(metadata)
        root_elem = self._write_assets(root_elem, assets)
        tree = etree.ElementTree(root_elem)
        with open(filename, 'w') as output_file:
            tree.write(output_file, xml_declaration=True,
                encoding='utf-8', pretty_print=True)

    def _value_defined_for(self, dict, attrib):
        return dict[attrib] != NO_VALUE

    def _write_header(self, metadata):
        root_elem = etree.Element(ROOT, nsmap=NSMAP)
        root_elem.attrib[GML_ID] = 'n1'
        exp_mod_elem = etree.SubElement(
            root_elem, EXPOSURE_MODEL)
        exp_mod_elem.attrib[GML_ID] = 'ep1'
        config = etree.SubElement(
            exp_mod_elem, CONFIG)
        exp_list_elem = etree.SubElement(
            exp_mod_elem, EXPOSURE_LIST)
        exp_list_elem.attrib[GML_ID] = metadata['expModId']

        if self._value_defined_for(metadata, 'assetCategory'):
            exp_list_elem.attrib[ASSET_CATEGORY] = metadata['assetCategory']
        else:
            raise RuntimeError('assetCategory is a compulsory value')

        if self._value_defined_for(metadata, 'areaType'):
            exp_list_elem.attrib[AREA_TYPE] = metadata['areaType']
        if self._value_defined_for(metadata, 'areaUnit'):
            exp_list_elem.attrib[AREA_UNIT] = metadata['areaUnit']
        if self._value_defined_for(metadata, 'cocoType'):
            exp_list_elem.attrib[COCO_TYPE] = metadata['cocoType']
        if self._value_defined_for(metadata, 'cocoUnit'):
            exp_list_elem.attrib[COCO_UNIT] = metadata['cocoUnit']
        if self._value_defined_for(metadata, 'recoType'):
            exp_list_elem.attrib[RECO_TYPE] = metadata['recoType']
        if self._value_defined_for(metadata, 'recoUnit'):
            exp_list_elem.attrib[RECO_UNIT] = metadata['recoUnit']
        if self._value_defined_for(metadata, 'stcoType'):
            exp_list_elem.attrib[STCO_TYPE] = metadata['stcoType']
        if self._value_defined_for(metadata, 'stcoUnit'):
            exp_list_elem.attrib[STCO_UNIT] = metadata['stcoUnit']
        if self._value_defined_for(metadata, 'description'):
            description = etree.SubElement(
                exp_list_elem, DESCRIPTION)
            description.text = metadata['description']
        if self._value_defined_for(metadata, 'taxonomySource'):
            taxonomy_source = etree.SubElement(
                exp_list_elem, TAXONOMY_SOURCE)
            taxonomy_source.text = metadata['taxonomySource']
        return root_elem

    def _write_assets(self, root_elem, assets):
        exp_list = root_elem.find('.//%s' % EXPOSURE_LIST)
        for i, asset in enumerate(assets, start=1):
            asset_elem = etree.SubElement(
                exp_list, ASSET)
            asset_elem.attrib[GML_ID] = 'asset_%s' % i

            if (self._value_defined_for(asset, 'lon') and
                self._value_defined_for(asset, 'lat')):

                site_elem = etree.SubElement(
                    asset_elem, SITE)
                point_elem = etree.SubElement(
                    site_elem, GML_POINT)
                point_elem.attrib[GML_SRS_ATTR_NAME] = GML_SRS_EPSG_4326
                pos_elem = etree.SubElement(
                    point_elem, GML_POS)
                pos_elem.text = " ".join([asset['lon'], asset['lat']])
            else:
               raise RuntimeError('lon and lat are compulsory values for an '
                                  'asset')

            if self._value_defined_for(asset, 'area'):
                area_elem = etree.SubElement(
                    asset_elem, AREA)
                area_elem.text = asset['area']

            if self._value_defined_for(asset, 'coco'):
                coco_elem = etree.SubElement(
                    asset_elem, COCO)
                coco_elem.text = asset['coco']

            if self._value_defined_for(asset, 'deductible'):
                deduct_elem = etree.SubElement(
                    asset_elem, DEDUCTIBLE)
                deduct_elem.text = asset['deductible']

            if self._value_defined_for(asset, 'limit'):
                limit_elem = etree.SubElement(
                    asset_elem, LIMIT)
                limit_elem.text = asset['limit']

            if self._value_defined_for(asset, 'number'):
                number_elem = etree.SubElement(
                    asset_elem, NUMBER)
                number_elem.text = asset['number']

            if self._value_defined_for(asset, 'occupantDay'):
                occupants_elem = etree.SubElement(
                    asset_elem, OCCUPANTS)
                occupants_elem.text = asset['occupantDay']
                occupants_elem.attrib['description'] = 'day'

            if self._value_defined_for(asset, 'occupantNight'):
                occupants_elem = etree.SubElement(
                    asset_elem, OCCUPANTS)
                occupants_elem.text = asset['occupantNight']
                occupants_elem.attrib['description'] = 'night'

            if self._value_defined_for(asset, 'reco'):
                reco_elem = etree.SubElement(
                    asset_elem, RECO)
                reco_elem.text = asset['reco']

            if self._value_defined_for(asset, 'stco'):
                stco_elem = etree.SubElement(
                    asset_elem, STCO)
                stco_elem.text = asset['stco']

            if self._value_defined_for(asset, 'taxonomy'):
                taxonomy_elem = etree.SubElement(
                    asset_elem, TAXONOMY)
                taxonomy_elem.text = asset['taxonomy']
            else:
                raise RuntimeError('taxonomy is a compulsory value for '
                                   'an asset')

        return root_elem
