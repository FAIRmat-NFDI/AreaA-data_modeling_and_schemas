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

from nomad.utils import hash

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    Section,
    MSection,
    Quantity,
)

from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad_material_processing import (
    Parallelepiped,
    SubstrateCrystalProperties,
    Miscut,
    Dopant,
)
from ikz_plugin import IKZMOVPECategory
from ikz_plugin.utils import create_archive
from ikz_plugin.movpe import (
    SubstrateInventory,
    SubstrateMovpe,
    SubstrateCrystalPropertiesMovpe,
    MiscutMovpe,
    SubstrateMovpeReference,
)
from .utils import (
    populate_element,
    populate_dopant,
)


class RawFileSubstrateInventory(EntryData):
    m_def = Section(a_eln=None, label="Raw File Substrate Inventory")
    measurement = Quantity(
        type=SubstrateInventory,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
        ),
    )


class MovpeSubstrateParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name="MOVPE Substrate IKZ",
            code_name="MOVPE Substrate IKZ",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        filetype = "yaml"
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        xlsx = pd.ExcelFile(mainfile)
        substrates_file = pd.read_excel(
            xlsx,
            "Substrate",
            comment="#",
        )
        substrates_file.columns = substrates_file.columns.str.strip()
        substrate_list = []
        for index, substrate_id in enumerate(substrates_file["Substrates"]):
            # creating Substrate archives
            substrate_filename = (
                f"{substrate_id}_{index}.SubstrateIKZ.archive.{filetype}"
            )
            substrate_data = SubstrateMovpe(
                lab_id=substrate_id,
                supplier=substrates_file["Supplier"][index],
                supplier_id=substrates_file["Polishing Number"][index],
                tags=[
                    substrates_file["Quality"][index],
                    substrates_file["Crystal"][index],
                ],
                as_received=substrates_file["As Received"][index],
                etching=substrates_file["Etching"][index],
                annealing=substrates_file["Annealing"][index],
                re_etching=substrates_file["Re-Etching"][index],
                epi_ready=substrates_file["Epi Ready"][index],
                quality=substrates_file["Quality"][index],
                description=str(substrates_file["Substrate Box"][index])
                + " "
                + str(substrates_file["Substrate Index"][index]),
                geometry=Parallelepiped(
                    width=substrates_file["Size X"][index],
                    length=substrates_file["Size Y"][index],
                ),
                crystal_properties=SubstrateCrystalPropertiesMovpe(
                    orientation=substrates_file["Orientation"][index],
                    miscut=MiscutMovpe(
                        b_angle=substrates_file["Miscut b angle"][index],
                        angle=substrates_file["Miscut c angle"][index],
                        orientation=substrates_file["Miscut c Orientation"][index],
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
                    reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, substrate_filename)}#data",
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
        inventory_filename = f"{data_file[:-5]}.archive.{filetype}"

        create_archive(
            inventory_archive.m_to_dict(),
            archive.m_context,
            inventory_filename,
            filetype,
            logger,
        )

        archive.data = RawFileSubstrateInventory(
            measurement=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, inventory_archive)}#data",
        )
        archive.metadata.entry_name = data_file + " substrates file"
