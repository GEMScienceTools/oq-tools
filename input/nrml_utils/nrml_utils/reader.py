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
