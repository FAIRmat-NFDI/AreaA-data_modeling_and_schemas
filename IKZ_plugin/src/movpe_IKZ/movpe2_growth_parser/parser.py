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
import yaml
import json


from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    MSection,
    Quantity,
    Section
)
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from nomad.datamodel.metainfo.basesections import (
    SystemComponent
)

from basesections_IKZ import IKZMOVPE2Category
from nomad.search import search
from nomad_material_processing.utils import create_archive as create_archive_ref
from movpe_IKZ import (
    Movpe2IKZExperiment,
    Movpe2Growths,
    Movpe2Growth,
    GrownSample
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.utils import hash


def create_archive(entry_dict, context, file_name, file_type, logger,*,bypass_check:bool=False):
    if not context.raw_path_exists(file_name) or bypass_check:
        with context.raw_file(file_name, 'w') as outfile:
            if file_type == 'json':
                json.dump(entry_dict, outfile)
            elif file_type == 'yaml':
                yaml.dump(entry_dict, outfile)
        context.upload.process_updated_raw_file(file_name, allow_modify=True)
    else:
        logger.error(
            f'{file_name} archive file already exists.'
            f'If you intend to reprocess the older archive file, remove the existing one and run reprocessing again.')


class RawFileGrowthRun(EntryData):
    m_def = Section(
        a_eln=None,
        categories=[IKZMOVPE2Category],
        label = 'Raw File Growth Run'
    )
    growth_runs = Quantity(
        type=Movpe2Growth,
        # a_eln=ELNAnnotation(
        #     component="ReferenceEditQuantity",
        # ),
        shape=['*']
    )


class Movpe2IKZParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name="MOVPE 2 IKZ",
            code_name="MOVPE 2 IKZ",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        grown_sample_ids = []
        growth_run_file = pd.read_excel(mainfile, comment="#")
        for sample_index, grown_sample in enumerate(growth_run_file["Sample Name"]):
            filetype = "yaml"
            grown_sample_ids.append(grown_sample)  # collect all ids
            filename = f"{grown_sample}_{sample_index}.archive.{filetype}"
            substrate_id = growth_run_file["Substrate Name"][sample_index]
            search_result = search(
                owner="all",
                query={"results.eln.sections:any": [
                        "Substrate"
                        ],
                        "results.eln.lab_ids:any": [
                        substrate_id
                        ]
                },
                user_id=archive.metadata.main_author.user_id,
            )
            if not search_result.data:
                grown_sample_object = GrownSample(
                    lab_id=grown_sample
                    )
                logger.warning(f'No Substrate entry with lab_id {substrate_id} was found, upload it and reprocess to have it referenced into the GrownSample entry with lab_id {grown_sample}')
            if len(search_result.data) > 1:
                logger.warning(f'Multiple Substrate entries with lab_id {substrate_id} were found, the first one was referenced into the GrownSample entry with lab_id {grown_sample}')
            if len(search_result.data) >= 1:
                grown_sample_object = GrownSample(
                    lab_id=grown_sample,
                    components=[SystemComponent(
                        system=f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
                        )
                    ]
                )
            grown_sample_archive = EntryArchive(
                data=grown_sample_object,
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
        tic = perf_counter()
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
            toc = perf_counter()
            if toc - tic > 15:
                logger.warning(f"The entry/ies with lab_id {grown_sample_ids} was not found and couldn't be referenced.")
                break

        growth_run_archive = EntryArchive(
            data=Movpe2Growth(data_file=data_file_with_path),
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
        tic = perf_counter()
        while True:
            search_result = search(
                owner="user",
                query={
                    "results.eln.sections:any": ["Movpe2Growth"],
                    "upload_id:any": [archive.m_context.upload_id]
                },
                user_id=archive.metadata.main_author.user_id,
                )
            lab_ids_current_mainfile = []
            growth_run_current_mainfile = []
            growth_run_current_recipe = []
            for growth_run_query_file in search_result.data:
                for search_quantities in growth_run_query_file['search_quantities']:
                    if (search_quantities['path_archive'] == "data.grown_sample.lab_id" and
                    search_quantities['str_value'] in list(growth_run_file["Sample Name"])
                    ):
                        lab_ids_current_mainfile.append(search_quantities['str_value'])
                        growth_run_current_mainfile.append(
                            f"../uploads/{archive.m_context.upload_id}/archive/{growth_run_query_file['entry_id']}#data"
                        )
                        growth_run_object = Movpe2Growths(
                            name=f"{search_quantities['str_value']} growth run",
                            reference=f"../uploads/{archive.m_context.upload_id}/archive/{growth_run_query_file['entry_id']}#data"
                        )
                        growth_run_current_recipe.append(growth_run_object)

            if sorted(lab_ids_current_mainfile) == sorted(growth_run_file["Sample Name"]):
                break
            sleep(0.1)
            toc = perf_counter()
            if toc - tic > 15:
                logger.warning("The Movpe2Growth entry/ies in the current upload were not found and couldn't be referenced.")
                break
        archive.data = RawFileGrowthRun(
            growth_runs=growth_run_current_mainfile
        )
        archive.metadata.entry_name = data_file + "raw file"

        recipe_ids = []
        for recipe_experiment in growth_run_file["Recipe Name"]:
            filetype = "yaml"
            recipe_ids.append(recipe_experiment)  # collect all ids
        recipe_ids = list(set(recipe_ids))  # remove duplicates

        for recipe_id in recipe_ids:
            filename = f"{recipe_id}.archive.{filetype}"
            if not archive.m_context.raw_path_exists(filename):
                experiment_data = Movpe2IKZExperiment(
                    lab_id=recipe_id,
                    growth_run=growth_run_current_recipe
                )
                experiment_archive = EntryArchive(
                    data=experiment_data,
                    #m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    experiment_archive.m_to_dict(),
                    archive.m_context,
                    filename,
                    filetype,
                    logger,
                )
            else: # the experiment file is being retrieved, extended, and overwritten
                with archive.m_context.raw_file(filename, 'r') as experiment_file:
                    updated_experiment = yaml.safe_load(experiment_file)
                    for new_growth_ref in growth_run_current_recipe:
                        updated_experiment['data']['growth_run'].append(new_growth_ref.m_to_dict())
                create_archive(
                    updated_experiment,
                    archive.m_context,
                    filename,
                    filetype,
                    logger,
                    bypass_check=True
                    )
