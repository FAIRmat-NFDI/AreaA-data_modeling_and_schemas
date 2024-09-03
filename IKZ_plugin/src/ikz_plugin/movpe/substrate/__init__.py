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


class SubstrateParserEntryPoint(ParserEntryPoint):
    def load(self):
        from ikz_plugin.movpe.substrate.parser import MovpeSubstrateParser

        return MovpeSubstrateParser(**self.dict())


parser = SubstrateParserEntryPoint(
    name='SubstrateParser',
    description='Parse excel files containing substrate parameters logged manually.',
    mainfile_name_re='.+\.substrates.movpe.ikz.xlsx',
    mainfile_mime_re='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    mainfile_contents_dict={
        'Substrate': {
            '__has_all_keys': ['Substrates', 'Crystal', 'Orientation', 'Elements']
        },
        '__comment_symbol': '#',
    },
)
