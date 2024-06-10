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

from nomad.config.models.plugins import ParserEntryPoint, SchemaPackageEntryPoint
from pydantic import Field


class DirSolEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from ikz_plugin.directional_solidification.schema import m_package

        return m_package


dir_sol_schema = DirSolEntryPoint(
    name='DirectionalSolidificationSchema',
    description='Schema package for Directional Solidification definitions.',
)


class DirSolManualProtocolParserEntryPoint(ParserEntryPoint):
    def load(self):
        from ikz_plugin.directional_solidification.parser import DSParserIKZ

        return DSParserIKZ(**self.dict())


dir_sol_manual_protocol_excel_parser = DirSolManualProtocolParserEntryPoint(
    name='DirSolManualProtocolParser',
    description='Parse excel files containing parameters from the process.',
    mainfile_name_re=r'.+\.ds.manualprotocol.xlsx',
    mainfile_mime_re='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
)
