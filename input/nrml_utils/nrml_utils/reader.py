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

from csv import DictReader


class ExposureTxtReader(object):


    ASSETS_FIELDNAMES = ['lon', 'lat', 'taxonomy', 'stco', 'number' ,'area',
                         'reco', 'coco', 'occupantDay', 'occupantNight',
                         'deductible', 'limit']

    def __init__(self, txtfile):
        self.txtfile = txtfile

    def _move_to_beginning_file(self):
        self.txtfile.seek(0)

    def _move_to_assets_definitions(self):
        self._move_to_beginning_file()
        while True:
            line = set([field.strip() for field in (
                self.txtfile.readline()).split(',')])
            if set(self.ASSETS_FIELDNAMES).issubset(line):
                break;

    @property
    def metadata(self):
        self._move_to_beginning_file()
        fieldnames = [field.strip() for field in (
            self.txtfile.readline()).split(',')]
        fieldvalues = [value.strip() for value in (
            self.txtfile.readline()).split(',')]
        return dict(zip(fieldnames, fieldvalues))

    def readassets(self):
        self._move_to_assets_definitions()
        reader = DictReader(self.txtfile, fieldnames=self.ASSETS_FIELDNAMES)
        return [asset for asset in reader]


class VulnerabilityTxtReader(object):

    FST_LINE_FIELDNAMES = ['vulnerabilitySetID', 'assetCategory',
                            'lossCategory', 'IMT']
    SND_LINE_FIELDNAME = 'IML'

    DISCRETE_VULNERABILITY_FIELDNAMES = ['vulnerabilityFunctionID',
                                         'probabilisticDistribution',
                                         'lossRatio', 'coefficientsVariation']

    def __init__(self, txtfile):
        self.txtfile = txtfile

    def _move_to_beginning_file(self):
        self.txtfile.seek(0)

    def _move_to_dscr_vuln_def(self):
        # It assumes that discreteVulnerability definitions
        # start from 4th line, so it's necessary to skip
        # the first three lines.
        self._move_to_beginning_file()
        lines_to_skip = 3
        for i in xrange(0, lines_to_skip):
            self.txtfile.readline()

    def _acquire_vuln_lines(self):
        lines = []
        for line in self.txtfile:
            lines.append(line.strip())
        if len(lines) % 3 != 0:
            raise RuntimeError('Every vulnerability is composed by three '
                           'lines: metadata, lossRatio, '
                           'coefficientVariations')
        return lines

    @property
    def metadata(self):
        self._move_to_beginning_file()
        fst_line_values = [field.strip() for field in
                           (self.txtfile.readline()).split(',')]
        metadata = dict(zip(self.FST_LINE_FIELDNAMES, fst_line_values))
        snd_line_iml_values = [field.strip() for field in
                               (self.txtfile.readline()).split(',')]
        metadata[self.SND_LINE_FIELDNAME] = snd_line_iml_values
        return metadata

    def readvulnerability(self):
        self._move_to_dscr_vuln_def()
        lines = self._acquire_vuln_lines()
        definitions = []
        for i in xrange(0, len(lines), 3):
            meta_values = lines[i].split(',')
            lossratio_values = lines[i + 1].split(',')
            coeffvar_values = lines[i + 2].split(',')
            vul_fn_id, prob_distr = meta_values[0], meta_values[1]
            vuln_def = dict(vulnerabilityFunctionId=vul_fn_id,
                            probabilityDistribution=prob_distr,
                            lossRatio=lossratio_values,
                            coefficientVariation=coeffvar_values)
            definitions.append(vuln_def)
        return definitions
