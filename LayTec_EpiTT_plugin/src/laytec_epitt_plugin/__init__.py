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

from nomad.config.models.plugins import SchemaPackageEntryPoint, ParserEntryPoint
from pydantic import Field


class LayTecEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from laytec_epitt_plugin.schema import m_package

        return m_package


laytec_schema = LayTecEntryPoint(
    name='LayTecSchema',
    description='Schema package defined using the new plugin mechanism.',
)


class LayTecParserEntryPoint(ParserEntryPoint):

    def load(self):
        from laytec_epitt_plugin.parser import EpiTTParser

        return EpiTTParser(**self.dict())


laytec_parser = LayTecParserEntryPoint(
    name='EpiTTParser',
    description='Parser for LayTec EpiTT files.',
    mainfile_name_re=r'.*\.dat',
    mainfile_contents_re='FILETYPE = EpiNet DatArchiver File',
)
