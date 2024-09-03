# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class Movpe2ParserEntryPoint(ParserEntryPoint):
    def load(self):
        from ikz_plugin.movpe.movpe2.growth_excel.parser import ParserMovpe2IKZ

        return ParserMovpe2IKZ(**self.dict())


parser = Movpe2ParserEntryPoint(
    name='Movpe2Parser',
    description='Parse excel files containing growth process parameters logged manually.',
    mainfile_name_re=r'.+\.growth.movpe.ikz.xlsx',
    mainfile_mime_re=r'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    mainfile_contents_dict={
        'GrowthRun': {'__has_all_keys': ['Sample Name']},
        '__comment_symbol': '#',
    },
)
