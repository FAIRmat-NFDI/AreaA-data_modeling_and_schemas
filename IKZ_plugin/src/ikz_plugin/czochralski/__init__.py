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


class CzochralskiSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from ikz_plugin.czochralski.schema import m_package

        return m_package


czochralski_schema = CzochralskiSchemaPackageEntryPoint(
    name='CzochralskiSchema',
    description='Schema package defined using the new plugin mechanism.',
)


class CzochralskiParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from ikz_plugin.czochralski.parser import CzParser

        return CzParser(**self.dict())


czochralski_multilog_parser = CzochralskiParserEntryPoint(
    name='CzochralskiParser',
    description='Parser defined using the new plugin mechanism.',
    mainfile_name_re=r'.+\.multilog.csv',
    mainfile_mime_re='text/csv',
)
