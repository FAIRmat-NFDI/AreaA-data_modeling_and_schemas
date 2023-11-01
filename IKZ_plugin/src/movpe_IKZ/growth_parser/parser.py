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

from time import sleep
import pandas as pd

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
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
from nomad.search import search
from nomad_material_processing.utils import create_archive as create_archive_ref
from movpe_IKZ import MovpeExperimentIKZ, GrowthRun, GrownSample
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing.tabular import create_archive
from nomad.utils import hash


class RawFile(EntryData):
    measurement = Quantity(
        type=GrowthRun,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
        ),
    )


class MovpeBinaryOxideIKZParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name="NOMAD movpe IKZ schema and parser plugin",
            code_name="movpe IKZ Parser",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        lab_ids = []
        growth_run_file = pd.read_excel(mainfile, comment="#")
        for sample_index, grown_sample in enumerate(growth_run_file["Sample Name"]):
            filetype = "yaml"
            lab_ids.append(grown_sample)  # collect all ids
            filename = f"{grown_sample}_{sample_index}.archive.{filetype}"
            grown_sample_archive = EntryArchive(
                data=GrownSample(lab_id=grown_sample),
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                grown_sample_archive.m_to_dict(),
                archive.m_context,
                filename,
                filetype,
                logger,
            )

        lab_ids = list(set(lab_ids))  # remove duplicates
        while True:
            search_result = search(
                owner="all",
                query={"results.eln.lab_ids": lab_ids},
                user_id=archive.metadata.main_author.user_id,
            )
            # checking if all entries are propery indexed
            if search_result.pagination.total == len(lab_ids):
                break
            # otherwise wait until all are indexed
            sleep(0.1)

        data_file = mainfile.split("/")[-1]
        entry = GrowthRun()
        entry.data_file = data_file
        file_name = f"{data_file[:-5]}.archive.json"
        archive.data = RawFile(
            measurement=create_archive_ref(entry, archive, file_name)
        )
        archive.metadata.entry_name = data_file + " growth file"
