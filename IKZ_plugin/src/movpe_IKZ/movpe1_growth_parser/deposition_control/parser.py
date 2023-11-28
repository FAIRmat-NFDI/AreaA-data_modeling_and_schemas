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

from time import (
    sleep,
    perf_counter
)
import pandas as pd
import re

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    Section,
    MSection,
    Quantity,
)
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad.search import search, MetadataPagination
from nomad_material_processing.utils import create_archive as create_archive_ref
from movpe_IKZ import (
    ExperimentMovpe1IKZ,
    DepositionControls,
    DepositionControlMovpe1IKZ,
    GrowthsMovpe1IKZ,
    GrowthMovpe1IKZ,
    GrownSample
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing.tabular import create_archive
from nomad.utils import hash

from basesections_IKZ import IKZMOVPE1Category

class RawFileDepositionControl(EntryData):
    m_def = Section(
        a_eln=None,
        categories=[IKZMOVPE1Category],
        label = 'Raw File Deposition Control'
    )
    deposition_control_file = Quantity(
        type=GrowthMovpe1IKZ,
        # a_eln=ELNAnnotation(
        #     component="ReferenceEditQuantity",
        # ),
        #shape=['*']
    )


class ParserMovpe1DepositionControlIKZ(MatchingParser):
    def __init__(self):
        super().__init__(
            name="MOVPE 1 Deposition Control IKZ",
            code_name="MOVPE 1 Deposition Control IKZ",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        filetype = "yaml"
        xlsx = pd.ExcelFile(mainfile)
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        dep_control = pd.read_excel(xlsx, 'Deposition Control', comment="#")
        dep_control.columns = [re.sub(r'\s+', ' ', col.strip()) for col in dep_control.columns]
        dep_control_filename = f"{dep_control['Sample ID'][0]}_deposition_control.archive.{filetype}"
        dep_control_archive = EntryArchive(
            data=DepositionControlMovpe1IKZ(data_file=data_file_with_path),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        create_archive(
            dep_control_archive.m_to_dict(),
            archive.m_context,
            dep_control_filename,
            filetype,
            logger,
        )

        tic = perf_counter()
        while True:
            search_result = search(
                owner="user",
                query={
                    "results.eln.sections:any": ["DepositionControlMovpe1IKZ"],
                    "upload_id:any": [archive.m_context.upload_id]
                },
                pagination=MetadataPagination(page_size=10000),
                user_id=archive.metadata.main_author.user_id,
                )
            # checking if all entries are properly indexed
            if search_result.pagination.total == len(dep_control['Sample ID']):
                break
            if search_result.pagination.total > len(dep_control['Sample ID']):
                matches = []
                for match in search_result.data:
                    matches.append(match['results']['eln']['lab_ids'])
                logger.warning(f'Some entries with lab_id {matches} are duplicated')
                break
            # otherwise wait until all are indexed
            sleep(0.1)
            toc = perf_counter()
            if toc - tic > 200:
                logger.warning(f"Some rows of 'deposition control' Excel file were not parsed. Please check the file and try again.")
                break
        if search_result.pagination.total == len(dep_control['Sample ID']):
            for deposition_control_entry in search_result.data:
                experiment_filename = f"{deposition_control_entry['results']['eln']['lab_ids'][0]}_experiment.archive.{filetype}"
                for row_index, row_id in enumerate(dep_control['Sample ID']):
                    if deposition_control_entry['results']['eln']['lab_ids'][0] == row_id:
                        constant_parameters_id=dep_control['Constant Parameters ID'][row_index]
                experiment_archive = EntryArchive(
                    data=ExperimentMovpe1IKZ(
                        lab_id=deposition_control_entry['results']['eln']['lab_ids'][0],
                        constant_parameters_id=constant_parameters_id,
                        deposition_control=DepositionControls(
                            reference=f"../uploads/{archive.m_context.upload_id}/archive/{deposition_control_entry['entry_id']}#data"
                        )
                    ),
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    experiment_archive.m_to_dict(),
                    archive.m_context,
                    experiment_filename,
                    filetype,
                    logger,
                )

        archive.data = RawFileDepositionControl(
            deposition_control_file=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, dep_control_filename)}#data"
        )
        #archive.metadata.entry_name = overview["Activity ID"][0] + "constant parameters file"

