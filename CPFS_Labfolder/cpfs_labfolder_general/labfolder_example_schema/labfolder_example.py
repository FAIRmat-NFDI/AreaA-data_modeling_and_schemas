#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)

m_package = Package(name='LabFolder Import Example')

class RepeatFromTable(ArchiveSection):
    name = Quantity(
        type=str
    )
    value = Quantity(
        type=float,
        unit='g'
    )

class SeparateArchive(EntryData):
    name = Quantity(
        type=str
    )
    value = Quantity(
        type=float,
        unit='s'
    )

class LabfolderImportExample(EntryData):
    quantity_1 = Quantity(
        type=float,
        unit='mm'
    )
    quantity_2 = Quantity(
        type=str
    )
    text_field = Quantity(
        type=str
    )
    from_table = SubSection(
        section_def=RepeatFromTable,
        repeats=True
    )
    reference = Quantity(
        type=SeparateArchive,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )

m_package.__init_metainfo__()