#
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
from typing import TYPE_CHECKING
from nomad.metainfo import (
    Quantity,
)
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from uv_vis_nir_transmission.utils import create_archive
from uv_vis_nir_transmission import ELNUVVisTransmission

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )


class RawFileUVVisTransmissionData(EntryData):
    """
    Section for a UV-Vis Transmission data file.
    """

    measurement = Quantity(
        type=ELNUVVisTransmission,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class UVVisTransmissionParser(MatchingParser):
    """
    Parser for matching UV-Vis-NIR Transmission files and creating instances of
    ELN
    """

    def __init__(self):
        super().__init__(
            code_name='UV-Vis-NIR Transmission Parser',
        )

    def parse(
        self, mainfile: str, archive: 'EntryArchive', logger=None, child_archives=None
    ) -> None:
        data_file = mainfile.split('/')[-1]
        entry = ELNUVVisTransmission.m_from_dict(ELNUVVisTransmission.m_def.a_template)
        entry.data_file = data_file
        file_name = f'{"".join(data_file.split(".")[:-1])}.archive.json'
        archive.data = RawFileUVVisTransmissionData(
            measurement=create_archive(entry, archive, file_name)
        )
        archive.metadata.entry_name = f'{data_file} data file'
