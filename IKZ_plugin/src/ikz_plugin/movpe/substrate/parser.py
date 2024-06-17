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

import pandas as pd
from nomad.datamodel.datamodel import EntryArchive
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.metainfo import (
    Quantity,
    Section,
)
from nomad.parsing import MatchingParser
from nomad.utils import hash
from nomad_material_processing import (
    Parallelepiped,
)

from nomad.datamodel.datamodel import EntryArchive, EntryMetadata

from ikz_plugin.movpe.schema import (
    MiscutMovpe,
    SubstrateCrystalPropertiesMovpe,
    SubstrateInventory,
    SubstrateMovpe,
    SubstrateMovpeReference,
)
from ikz_plugin.utils import (
    create_archive,
    typed_df_value,
)

from .utils import (
    populate_dopant,
    populate_element,
)


class RawFileSubstrateInventory(EntryData):
    m_def = Section(a_eln=None, label='Raw File Substrate Inventory')
    measurement = Quantity(
        type=SubstrateInventory,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class MovpeSubstrateParser(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        filetype = 'yaml'
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split('raw/')[-1]
        xlsx = pd.ExcelFile(mainfile)
        substrates_file = pd.read_excel(
            xlsx,
            'Substrate',
            comment='#',
        )
        substrates_file.columns = substrates_file.columns.str.strip()
        substrate_list = []
        for index, substrate_id in enumerate(substrates_file['Substrates']):
            # creating Substrate archives
            substrate_filename = (
                f'{substrate_id}_{index}.SubstrateIKZ.archive.{filetype}'
            )
            substrate_data = SubstrateMovpe(
                lab_id=substrate_id,
                supplier=(typed_df_value(substrates_file, 'Supplier', str, index)),
                supplier_id=(
                    typed_df_value(substrates_file, 'Polishing Number', str, index)
                ),
                tags=[
                    typed_df_value(substrates_file, 'Quality', str, index),
                    typed_df_value(substrates_file, 'Crystal', str, index),
                ],
                as_received=(
                    typed_df_value(substrates_file, 'As Received', bool, index)
                ),
                etching=(typed_df_value(substrates_file, 'Etching', bool, index)),
                annealing=(typed_df_value(substrates_file, 'Annealing', bool, index)),
                re_etching=(typed_df_value(substrates_file, 'Re-Etching', bool, index)),
                epi_ready=(typed_df_value(substrates_file, 'Epi Ready', bool, index)),
                quality=(typed_df_value(substrates_file, 'Quality', bool, index)),
                description=f"{typed_df_value(substrates_file, 'Substrate Box', bool, index)} {typed_df_value(substrates_file, 'Substrate Index', bool, index)}",
                geometry=Parallelepiped(
                    width=(typed_df_value(substrates_file, 'Size X', float, index)),
                    length=(typed_df_value(substrates_file, 'Size Y', float, index)),
                ),
                crystal_properties=SubstrateCrystalPropertiesMovpe(
                    orientation=(
                        typed_df_value(substrates_file, 'Orientation', str, index)
                    ),
                    miscut=MiscutMovpe(
                        b_angle=(
                            typed_df_value(
                                substrates_file, 'Miscut b angle', float, index
                            )
                        ),
                        angle=(
                            typed_df_value(
                                substrates_file, 'Miscut c angle', float, index
                            )
                        ),
                        orientation=(
                            typed_df_value(
                                substrates_file, 'Miscut c Orientation', str, index
                            )
                        ),
                    ),
                ),
                elemental_composition=populate_element(index, substrates_file),
                dopants=populate_dopant(index, substrates_file),
            )

            substrate_archive = EntryArchive(
                data=substrate_data,
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                substrate_archive.m_to_dict(),
                archive.m_context,
                substrate_filename,
                filetype,
                logger,
            )
            substrate_list.append(
                SubstrateMovpeReference(
                    reference=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, substrate_filename)}#data',
                )
            )
        invenroty_data = SubstrateInventory(
            data_file=data_file_with_path,
            substrates=substrate_list,
        )
        inventory_archive = EntryArchive(
            data=invenroty_data,
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        inventory_filename = f'{data_file[:-5]}.archive.{filetype}'

        create_archive(
            inventory_archive.m_to_dict(),
            archive.m_context,
            inventory_filename,
            filetype,
            logger,
        )

        archive.data = RawFileSubstrateInventory(
            measurement=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, inventory_archive)}#data',
        )
        archive.metadata.entry_name = data_file + ' substrates file'
