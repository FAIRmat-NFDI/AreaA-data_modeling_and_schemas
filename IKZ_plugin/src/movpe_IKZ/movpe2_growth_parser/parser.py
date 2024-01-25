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

from time import sleep, perf_counter
import pandas as pd
import yaml
import json
from typing import Dict, List


from nomad.datamodel import EntryArchive
from nomad.metainfo import MSection, Quantity, Section
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from nomad.datamodel.metainfo.basesections import SystemComponent

from basesections_IKZ import IKZMOVPE2Category
from nomad.search import search
from nomad_material_processing.utils import create_archive as create_archive_ref
from movpe_IKZ import (
    ExperimentMovpe2IKZ,
    GrowthMovpe2IKZ,
    GrownSample,
    GrownSampleReference,
    ParentSampleReference,
    SubstrateReference,
    GrowthStepMovpe2IKZ,
    Bubbler,
    GasSource,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.utils import hash


def create_archive(
    entry_dict, context, file_name, file_type, logger, *, bypass_check: bool = False
):
    if not context.raw_path_exists(file_name) or bypass_check:
        with context.raw_file(file_name, "w") as outfile:
            if file_type == "json":
                json.dump(entry_dict, outfile)
            elif file_type == "yaml":
                yaml.dump(entry_dict, outfile)
        context.upload.process_updated_raw_file(file_name, allow_modify=True)
    else:
        logger.error(
            f"{file_name} archive file already exists."
            f"If you intend to reprocess the older archive file, remove the existing one and run reprocessing again."
        )


class RawFileGrowthRun(EntryData):
    m_def = Section(
        a_eln=None, categories=[IKZMOVPE2Category], label="Raw File Growth Run"
    )
    growth_runs = Quantity(
        type=ExperimentMovpe2IKZ,
        # a_eln=ELNAnnotation(
        #     component="ReferenceEditQuantity",
        # ),
        shape=["*"],
    )


class ParserMovpe2IKZ(MatchingParser):
    def __init__(self):
        super().__init__(
            name="MOVPE 2 IKZ",
            code_name="MOVPE 2 IKZ",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        filetype = "yaml"
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        grown_sample_ids = []
        growth_run_file = pd.read_excel(mainfile, comment="#")

        # creating experiment dict
        growth_process_list: Dict[str, GrowthMovpe2IKZ] = {}
        recipe_ids = [
            recipe_experiment for recipe_experiment in growth_run_file["Recipe Name"]
        ]
        recipe_ids = list(set(recipe_ids))  # remove duplicates
        for unique_id in recipe_ids:
            growth_process_list[unique_id] = []

        # creating grown sample archives and growth process archives
        for index, grown_sample in enumerate(growth_run_file["Sample Name"]):
            # creating grown sample archives
            grown_sample_ids.append(grown_sample)  # collect all ids
            grown_sample_filename = (
                f"{grown_sample}_{index}.GrownSample.archive.{filetype}"
            )
            substrate_id = growth_run_file["Substrate Name"][index]
            substrate_reference_str = None
            search_result = search(
                owner="all",
                query={
                    "results.eln.sections:any": ["SubstrateMovpe", "Substrate"],
                    "results.eln.lab_ids:any": [substrate_id],
                },
                user_id=archive.metadata.main_author.user_id,
            )
            if not search_result.data:
                grown_sample_data = GrownSample(lab_id=grown_sample)
                logger.warning(
                    f"Substrate entry [{substrate_id}] was not found, upload and reprocess to reference it in GrownSample entry [{grown_sample}]"
                )
            if len(search_result.data) > 1:
                logger.warn(
                    f"Found {search_result.pagination.total} entries with lab_id: "
                    f'"{substrate_id}". Will use the first one found.'
                )
            if len(search_result.data) >= 1:
                substrate_reference_str = f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
                grown_sample_data = GrownSample(
                    lab_id=grown_sample,
                    components=[SystemComponent(system=substrate_reference_str)],
                )
            grown_sample_archive = EntryArchive(
                data=grown_sample_data,
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                grown_sample_archive.m_to_dict(),
                archive.m_context,
                grown_sample_filename,
                filetype,
                logger,
            )
            # creating bubblers objects
            bubblers = []
            bubbler_quantities = [
                "Bubbler Material",
                "Bubbler MFC",
                "Bubbler Pressure",
                "Bubbler Dilution",
                "Source",
                "Inject",
                "Bubbler Temp",
                "Bubbler Partial Pressure",
                "Bubbler Molar Flux",
            ]
            i = 0
            while True:
                if all(
                    f"{key}{'' if i == 0 else '.' + str(i)}" in growth_run_file.columns
                    for key in bubbler_quantities
                ):
                    bubblers.append(
                        Bubbler(
                            name=growth_run_file.get(
                                f"Bubbler Material{'' if i == 0 else '.' + str(i)}", ""
                            )[index],
                            mass_flow_controller=growth_run_file.get(
                                f"Bubbler MFC{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                            pressure=growth_run_file.get(
                                f"Bubbler Pressure{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                            dilution=growth_run_file.get(
                                f"Bubbler Dilution{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                            source=growth_run_file.get(
                                f"Source{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                            inject=growth_run_file.get(
                                f"Inject{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                            temperature=growth_run_file.get(
                                f"Bubbler Temp{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                            partial_pressure=growth_run_file.get(
                                f"Bubbler Partial Pressure{'' if i == 0 else '.' + str(i)}",
                                0,
                            )[index],
                            molar_flux=growth_run_file.get(
                                f"Bubbler Molar Flux{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                        )
                    )
                    i += 1
                else:
                    break

            # creating growth process objects
            growth_process_instance = GrowthMovpe2IKZ(
                name=f"{grown_sample} growth run",
                recipe_id=growth_run_file["Recipe Name"][index],
                lab_id=f"{grown_sample} growth run",
                samples=[
                    GrownSampleReference(
                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, grown_sample_filename)}#data",
                    )
                ],
                substrate=[
                    SubstrateReference(
                        lab_id=growth_run_file["Substrate Name"][index],
                    )
                ],
                parent_sample=[
                    ParentSampleReference(
                        lab_id=growth_run_file["Previous Layer Name"][index],
                    )
                ],
                steps=[
                    GrowthStepMovpe2IKZ(
                        name=growth_run_file["Step name"][index],
                        step_index=growth_run_file["Step Index"][index],
                        elapsed_time=growth_run_file["Duration"][index],
                        temperature_shaft=growth_run_file["T Shaft"][index],
                        temperature_filament=growth_run_file["T Filament"][index],
                        temperature_laytec=growth_run_file["T LayTec"][index],
                        pressure=growth_run_file["Pressure"][index],
                        rotation=growth_run_file["Rotation"][index],
                        carrier_gas=growth_run_file["Carrier Gas"][index],
                        push_gas_valve=growth_run_file["Pushgas Valve"][index],
                        uniform_valve=growth_run_file["Uniform Valve"][index],
                        showerhead_distance=growth_run_file["Distance of Showerhead"][
                            index
                        ],
                        comments=growth_run_file["Comments"][index],
                        bubblers=bubblers,
                    )
                ],
            )
            growth_process_list[growth_run_file["Recipe Name"][index]].append(
                growth_process_instance
            )

        experiment_reference = []
        for unique_id in recipe_ids:
            experiment_filename = f"{unique_id}.archive.{filetype}"
            experiment_data = ExperimentMovpe2IKZ(
                lab_id=unique_id,
                growth_runs=growth_process_list[unique_id],
            )
            experiment_archive = EntryArchive(
                data=experiment_data,
                # m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                experiment_archive.m_to_dict(),
                archive.m_context,
                experiment_filename,
                filetype,
                logger,
            )
            experiment_reference.append(
                f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, experiment_filename)}#data"
            )

        archive.data = RawFileGrowthRun(growth_runs=experiment_reference)
        archive.metadata.entry_name = data_file + "raw file"
