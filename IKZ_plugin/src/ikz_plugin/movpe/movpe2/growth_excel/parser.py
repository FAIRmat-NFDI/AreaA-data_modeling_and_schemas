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

from nomad.units import ureg

from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.utils import hash
from nomad.metainfo import MSection, Quantity, Section
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from nomad.datamodel.metainfo.basesections import (
    SystemComponent,
    PubChemPureSubstanceSection,
)

# from nomad_material_processing.utils import create_archive as create_archive_ref
from nomad_material_processing import (
    SubstrateReference,
    ThinFilmReference,
)

from nomad_material_processing.chemical_vapor_deposition import (
    Pressure,
    Rotation,
    VolumeFlowRate,
)

from ikz_plugin.movpe import (
    ExperimentMovpeIKZ,
    GrowthStepMovpe2IKZ,
    GrowthMovpeIKZ,
    GrowthMovpeIKZReference,
    ThinFilmMovpe,
    ThinFilmStackMovpe,
    ThinFilmStackMovpeReference,
    SampleParametersMovpe,
    ChamberEnvironmentMovpe,
    ShaftTemperature,
    FilamentTemperature,
    LayTecTemperature,
)

from ikz_plugin.utils import create_archive

from ..utils import (
    fetch_substrate,
    populate_sources,
    populate_gas_source,
)


class RawFileGrowthRun(EntryData):
    m_def = Section(a_eln=None, label="Raw File Growth Run")
    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    growth_runs = Quantity(
        type=ExperimentMovpeIKZ,
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
        """
        Parses the MOVPE 2 IKZ raw file and creates the corresponding archives.
        """

        filetype = "yaml"
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        growth_run_file = pd.read_excel(mainfile, comment="#")
        recipe_ids = list(
            set(
                growth_run_file["Recipe Name"]
                if "Recipe Name" in growth_run_file.columns
                else None
            )
        )

        # initializing experiments dict
        growth_processes: Dict[str, GrowthMovpeIKZ] = {}
        # initializing steps dict
        process_steps_lists: Dict[str, Dict[str, GrowthStepMovpe2IKZ]] = {}
        # initializing samples dict
        samples_lists: Dict[str, Dict[str, List]] = {}

        for index, sample_id in enumerate(growth_run_file["Sample Name"]):
            recipe_id = (
                growth_run_file["Recipe Name"][index]
                if "Recipe Name" in growth_run_file.columns
                else None
            )
            step_id = (
                growth_run_file["Step Index"][index]
                if "Step Index" in growth_run_file.columns
                else None
            )
            substrate_id = (
                growth_run_file["Substrate Name"][index]
                if "Substrate Name" in growth_run_file.columns
                else None
            )

            # creating ThinFiln and ThinFilmStack archives
            layer_filename = f"{sample_id}_{index}.ThinFilm.archive.{filetype}"
            layer_archive = EntryArchive(
                data=ThinFilmMovpe(
                    name=sample_id + " layer",
                    lab_id=sample_id + "layer",
                ),
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                layer_archive.m_to_dict(),
                archive.m_context,
                layer_filename,
                filetype,
                logger,
            )
            grown_sample_data = ThinFilmStackMovpe(
                name=sample_id + " stack",
                lab_id=sample_id,
                layers=[
                    ThinFilmReference(
                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, layer_filename)}#data"
                    )
                ],
            )
            substrate_ref = fetch_substrate(archive, sample_id, substrate_id, logger)
            if substrate_ref is not None:
                grown_sample_data.substrate = SubstrateReference(
                    reference=substrate_ref
                )
            else:
                grown_sample_data.substrate = SubstrateReference(lab_id=substrate_id)
            grown_sample_filename = (
                f"{sample_id}_{index}.ThinFilmStack.archive.{filetype}"
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
            # creating sample objects (for each process step)
            if recipe_id not in samples_lists:
                samples_lists[recipe_id] = {}
            if step_id not in samples_lists[recipe_id]:
                samples_lists[recipe_id][step_id] = []
            samples_lists[recipe_id][step_id].append(
                SampleParametersMovpe(
                    layer=ThinFilmReference(
                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, layer_filename)}#data",
                    ),
                    substrate=ThinFilmStackMovpeReference(
                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, grown_sample_filename)}#data",
                    ),
                    distance_to_source=[
                        (
                            growth_run_file["Distance of Showerhead"][index]
                            if "Distance of Showerhead" in growth_run_file.columns
                            else None
                        )
                        * ureg("millimeter").to("meter").magnitude
                    ],
                    shaft_temperature=ShaftTemperature(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["T Shaft"][index]
                                    if "T Shaft" in growth_run_file.columns
                                    else None
                                )
                            ]
                        ),
                    ),
                    filament_temperature=FilamentTemperature(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["T Filament"][index]
                                    if "T Filament" in growth_run_file.columns
                                    else None
                                )
                            ]
                        ),
                    ),
                    laytec_temperature=LayTecTemperature(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["T LayTec"][index]
                                    if "T LayTec" in growth_run_file.columns
                                    else None
                                )
                            ]
                        ),
                    ),
                )
            )

            # creating growth process step objects
            if recipe_id not in process_steps_lists:
                process_steps_lists[recipe_id] = {}
            if step_id not in process_steps_lists[recipe_id]:
                process_steps_lists[recipe_id][step_id] = []
            process_steps_lists[recipe_id][step_id] = GrowthStepMovpe2IKZ(
                name=str(
                    growth_run_file["Step name"][index]
                    if "Step name" in growth_run_file.columns
                    else None
                )
                + " step "
                + str(step_id),
                step_index=step_id,
                duration=(
                    growth_run_file["Duration"][index]
                    if "Duration" in growth_run_file.columns
                    else None * ureg("minute").to("second").magnitude
                ),
                comment=(
                    growth_run_file["Comments"][index]
                    if "Comments" in growth_run_file.columns
                    else None
                ),
                sources=populate_sources(index, growth_run_file)
                + populate_gas_source(index, growth_run_file),
                environment=ChamberEnvironmentMovpe(
                    pressure=Pressure(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["Pressure"][index]
                                    if "Pressure" in growth_run_file.columns
                                    else None
                                )
                            ]
                        )
                        * ureg("mbar").to("pascal").magnitude,
                    ),
                    rotation=Rotation(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["Rotation"][index]
                                    if "Rotation" in growth_run_file.columns
                                    else None
                                )
                            ]
                        )
                        * ureg("rpm").to("rpm").magnitude,
                    ),
                    carrier_gas=PubChemPureSubstanceSection(
                        name=(
                            growth_run_file["Carrier Gas"][index]
                            if "Carrier Gas" in growth_run_file.columns
                            else None
                        ),
                    ),
                    carrier_push_valve=VolumeFlowRate(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["Pushgas Valve"][index]
                                    if "Pushgas Valve" in growth_run_file.columns
                                    else None
                                )
                            ]
                        )
                        * ureg("cm ** 3 / minute").to("meter ** 3 / second").magnitude,
                    ),
                    uniform_valve=VolumeFlowRate(
                        set_value=pd.Series(
                            [
                                (
                                    growth_run_file["Uniform Valve"][index]
                                    if "Uniform Valve" in growth_run_file.columns
                                    else None
                                )
                            ]
                        )
                        * ureg("cm ** 3 / minute").to("meter ** 3 / second").magnitude,
                    ),
                ),
            )
            # else:
            #     ### IMPLEMENT THE CHECK OF STEP PARAMETERS
            #     pass

            # creating growth process objects
            if recipe_id not in growth_processes:
                growth_processes[recipe_id] = GrowthMovpeIKZ(
                    name="Growth MOVPE 2",
                    recipe_id=recipe_id,
                    lab_id=sample_id,
                )
            # else:
            #     ### IMPLEMENT THE CHECK OF STEP PARAMETERS
            #     pass

        # composing the growth process STEPS objects
        for recipe_id, samples_dict in samples_lists.items():
            if recipe_id in process_steps_lists:
                for step_id, samples_list in samples_dict.items():
                    if step_id in process_steps_lists[recipe_id]:
                        process_steps_lists[recipe_id][
                            step_id
                        ].sample_parameters.extend(samples_list)

        # composing the growth process objects
        for recipe_id, process_dict in process_steps_lists.items():
            if recipe_id in growth_processes:
                for _, process_list in process_dict.items():
                    growth_processes[recipe_id].steps.append(process_list)
            else:
                logger.error(
                    f"The GrowthMovpeIKZ object with lab_id '{recipe_id}' was not found."
                )
        # creating growth process archives
        for recipe_id, growth_process_object in growth_processes.items():
            growth_process_filename = f"{recipe_id}.GrowthMovpeIKZ.archive.{filetype}"
            # Activity.normalize(growth_process_object, archive, logger)
            growth_process_archive = EntryArchive(
                data=growth_process_object,
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )

            create_archive(
                growth_process_archive.m_to_dict(),
                archive.m_context,
                growth_process_filename,
                filetype,
                logger,
            )

        experiment_reference = []
        for recipe_id in recipe_ids:
            experiment_filename = f"{recipe_id}.ExperimentMovpeIKZ.archive.{filetype}"
            growth_process_filename = f"{recipe_id}.GrowthMovpeIKZ.archive.{filetype}"
            experiment_data = ExperimentMovpeIKZ(
                name=f"{recipe_id} experiment",
                method="MOVPE 2 experiment",
                lab_id=recipe_id,
                growth_run=GrowthMovpeIKZReference(
                    reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, growth_process_filename)}#data",
                ),
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

        archive.data = RawFileGrowthRun(
            name=data_file, growth_runs=experiment_reference
        )
        archive.metadata.entry_name = data_file + "raw file"
