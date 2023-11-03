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
from movpe_IKZ import (
    MovpeBinaryOxidesIKZExperiment,
    GrowthRuns,
    GrowthRun,
    GrownSample
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing.tabular import create_archive
from nomad.utils import hash


class RawFile(EntryData):
    grwoth_runs = Quantity(
        type=GrowthRun,
        # a_eln=ELNAnnotation(
        #     component="ReferenceEditQuantity",
        # ),
        shape=['*']
    )


class MovpeBinaryOxidesIKZParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name="NOMAD binary oxides growth movpe IKZ schema and parser plugin",
            code_name="binary oxides growth movpe IKZ parser",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        grown_sample_ids = []
        growth_run_file = pd.read_excel(mainfile, comment="#")
        for sample_index, grown_sample in enumerate(growth_run_file["Sample Name"]):
            filetype = "yaml"
            grown_sample_ids.append(grown_sample)  # collect all ids
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

        grown_sample_ids = list(set(grown_sample_ids))  # remove duplicates
        while True:
            search_result = search(
                owner="all",
                query={"results.eln.lab_ids:any": grown_sample_ids},
                user_id=archive.metadata.main_author.user_id,
            )
            # checking if all entries are properly indexed
            if search_result.pagination.total == len(grown_sample_ids):
                break
            if search_result.pagination.total > len(grown_sample_ids):
                matches = []
                for match in search_result.data:
                    matches.append(match['results']['eln']['lab_ids'])
                logger.warning(f'Some entries with lab_id {matches} are duplicated')
                break
            # otherwise wait until all are indexed
            sleep(0.1)

        data_file = mainfile.split("/")[-1]
        growth_run_archive = EntryArchive(
            data=GrowthRun(data_file=data_file),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        file_name = f"{data_file[:-5]}.archive.{filetype}"
        create_archive(
            growth_run_archive.m_to_dict(),
            archive.m_context,
            file_name,
            filetype,
            logger
        )
        #archive.m_context.process_updated_raw_file(file_name)
        while True:
            search_result = search(
                owner="user",
                query={
                    "results.eln.sections:any": ["GrowthRun"],
                    "upload_id:any": [archive.m_context.upload_id]
                },
                user_id=archive.metadata.main_author.user_id,
                )
            if search_result.pagination.total == len(growth_run_file["Sample Name"]): # or search_result.data['processing_errors']:  TODO !!!! check for errors !!!
                break
            sleep(0.1)
        if search_result.data:
            growth_run_files = []
            for growth_run_entry in search_result.data:
                growth_run_files.append(
                    f"../uploads/{archive.m_context.upload_id}/archive/{growth_run_entry['entry_id']}#data"
                    )
        archive.data = RawFile(
            grwoth_runs=growth_run_files
        )
        archive.metadata.entry_name = data_file + "raw file"

        recipe_ids = []
        for recipe_experiment in growth_run_file["Recipe Name"]:
            filetype = "yaml"
            recipe_ids.append(recipe_experiment)  # collect all ids
        recipe_ids = list(set(recipe_ids))  # remove duplicates

        for recipe_index, recipe_id in enumerate(recipe_ids):
            filename = f"{recipe_id}_{recipe_index}.archive.{filetype}"
            growth_run_samerecipe_files = []
            for growth_run_file in search_result.data:
                if growth_run_file['results']['eln']['lab_ids'][0] == recipe_id:
                    search_result = search(
                        owner="user",
                        query={
                            "results.eln.sections:any": ["GrowthRun"],
                            "entry_id:any": [growth_run_entry['entry_id']]
                        },
                        user_id=archive.metadata.main_author.user_id,
                        )

                    for search_quantities in search_result.data[0]['search_quantities']:
                        if search_quantities['path_archive'] == "data.grown_sample.lab_id":
                            growth_run_object_name = f"{search_quantities['str_value']} growth run"
                    growth_run_object = GrowthRuns(
                        name=growth_run_object_name,
                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{growth_run_file['entry_id']}#data"
                        )
                    growth_run_samerecipe_files.append(growth_run_object)
            experiment_data = MovpeBinaryOxidesIKZExperiment(
                lab_id=recipe_id,
                growth_run=growth_run_samerecipe_files
            )
            experiment_archive = EntryArchive(
                data=experiment_data,
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                experiment_archive.m_to_dict(),
                archive.m_context,
                filename,
                filetype,
                logger,
            )
