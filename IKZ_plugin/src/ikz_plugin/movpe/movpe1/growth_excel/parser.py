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
import re
import yaml
import json

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    Section,
    SubSection,
    Quantity,
)
from nomad.units import ureg

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)
from nomad.parsing import MatchingParser
from nomad.datamodel.context import ServerContext
from nomad.processing.data import Upload
from nomad.app.v1.models.models import User
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.search import search, MetadataPagination
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.utils import hash

from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    PureSubstanceComponent,
    PureSubstanceSection,
)

from nomad_material_processing import (
    SubstrateReference,
    ThinFilmReference,
)

from nomad_material_processing.chemical_vapor_deposition import (
    Pressure,
    Rotation,
)

from ikz_plugin import IKZMOVPE1Category, Solution
from ikz_plugin.utils import (
    create_archive,
    row_to_array,
)
from ikz_plugin.movpe import (
    ExperimentMovpeIKZ,
    GrowthMovpeIKZReference,
    GrowthMovpeIKZ,
    GrowthStepMovpe1IKZ,
    PrecursorsPreparationIKZ,
    PrecursorsPreparationIKZReference,
    ThinFilmStackMovpeReference,
    ThinFilmStackMovpe,
    LiquidComponent,
    SystemComponentIKZ,
    ChamberEnvironmentMovpe,
    FilamentTemperature,
    FlashEvaporator1Pressure,
    FlashEvaporator2Pressure,
    OxygenTemperature,
    ShaftTemperature,
    ThrottleValve,
    RawFileMovpeDepositionControl,
)

from ikz_plugin.movpe.movpe1.utils import create_timeseries_objects


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
        dep_control = pd.read_excel(xlsx, "Deposition Control", comment="#")
        precursors = pd.read_excel(xlsx, "Precursors", comment="#")
        dep_control.columns = [
            re.sub(r"\s+", " ", col.strip()) for col in dep_control.columns
        ]
        precursors.columns = [
            re.sub(r"\s+", " ", col.strip()) for col in precursors.columns
        ]
        deposition_control_list = []

        if not len(dep_control["Sample ID"]) == len(precursors["Sample ID"]):
            logger.error(
                f"Excel sheets mismatch: "
                f"'Deposition Control' has {len(dep_control['Sample ID'])} rows "
                f"and 'Precursors' has {len(precursors['Sample ID'])} rows. "
                f"Please check the file and try again."
            )

        for index, dep_control_run in enumerate(dep_control["Sample ID"]):
            assert dep_control_run == precursors["Sample ID"][index], (
                f"Not matching Sample ID at line {index} in "
                f"'deposition control' [{dep_control_run}] "
                f"and 'precursors' [{precursors['Sample ID'][index]}] sheets."
                f"Please check the files and try again."
            )

            # check if experiment archive exists already
            search_experiments = search(
                owner="user",
                query={
                    "results.eln.sections:any": ["ExperimentMovpeIKZ"],
                },
                pagination=MetadataPagination(page_size=10000),
                user_id=archive.metadata.main_author.user_id,
            )
            # check if experiment entries are already indexed
            matches = {
                "lab_id": [],
                "entry_id": [],
                "entry_name": [],
                "upload_id": [],
            }
            if search_experiments.pagination.total >= 1:
                for match in search_experiments.data:
                    if (
                        f"{dep_control_run} experiment"
                        in match["results"]["eln"]["lab_ids"]
                    ):
                        matches["lab_id"].extend(match["results"]["eln"]["lab_ids"])
                        matches["entry_id"].append(match["entry_id"])
                        matches["entry_name"].append(match["entry_name"])
                        matches["upload_id"].append(match["upload_id"])
                if len(matches["entry_id"]) == 1:
                    logger.warning(
                        f"One entry with lab_id {set(matches['lab_id'])} and entry_id {set(matches['entry_id'])} already exists. "
                        f"Please check the upload with upload id {set(matches['upload_id'])}."
                    )
                    continue
                elif len(matches["entry_id"]) > 1:
                    logger.warning(
                        f"Some entries with lab_id {set(matches['lab_id'])} and entry_id {set(matches['entry_id'])} are duplicated. Please check them."
                    )
                    continue
            elif search_experiments.pagination.total == 0:
                # create grown sample archive
                sample_filename = (
                    f"{dep_control_run}.ThinFilmStackMovpe.archive.{filetype}"
                )
                sample_archive = EntryArchive(
                    data=ThinFilmStackMovpe(
                        lab_id=dep_control_run,
                        substrate=SubstrateReference(
                            lab_id=dep_control["Substrate ID"][index],
                        ),
                    ),
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    sample_archive.m_to_dict(),
                    archive.m_context,
                    sample_filename,
                    filetype,
                    logger,
                )

                filament_temperatures = create_timeseries_objects(
                    dep_control, ["Fil time", "Fil T"], FilamentTemperature, index
                )
                flash_evaporator1_pressures = create_timeseries_objects(
                    dep_control,
                    ["BP FE1 time", "BP FE1"],
                    FlashEvaporator1Pressure,
                    index,
                )
                flash_evaporator2_pressures = create_timeseries_objects(
                    dep_control,
                    ["BP FE2 time", "BP FE2"],
                    FlashEvaporator2Pressure,
                    index,
                )
                oxygen_temperatures = create_timeseries_objects(
                    dep_control,
                    ["Oxygen time", "Oxygen T"],
                    OxygenTemperature,
                    index,
                )
                shaft_temperatures = create_timeseries_objects(
                    dep_control,
                    ["Oxygen time", "Oxygen T"],
                    ShaftTemperature,
                    index,
                )
                throttle_valves = create_timeseries_objects(
                    dep_control, ["Oxygen time", "Oxygen T"], ThrottleValve, index
                )

                # creating GrowthMovpeIKZ archive
                growth_data = GrowthMovpeIKZ(
                    data_file=data_file_with_path,
                    name="Growth MOVPE 1",
                    lab_id=dep_control_run,
                    description=f"{dep_control['Weekday'][index]}. Sequential number: {dep_control['number'][index]}. {dep_control['Comment'][index]}",
                    datetime=dep_control["Date"][index],
                    steps=[
                        GrowthStepMovpe1IKZ(
                            name="Deposition",
                            duration=dep_control["Duration"][index],
                            filament_temperature=filament_temperatures,
                            flash_evaporator1_pressure=flash_evaporator1_pressures,
                            flash_evaporator2_pressure=flash_evaporator2_pressures,
                            oxygen_temperature=oxygen_temperatures,
                            shaft_temperature=shaft_temperatures,
                            throttle_valve=throttle_valves,
                            environment=ChamberEnvironmentMovpe(
                                pressure=Pressure(
                                    set_value=dep_control["Set Chamber P"][index],
                                    value=row_to_array(
                                        dep_control,
                                        ["Read Chamber Pressure"],
                                        index,
                                    ),
                                    time=row_to_array(
                                        dep_control,
                                        ["Chamber pressure time"],
                                        index,
                                    ),
                                ),
                                rotation=Rotation(
                                    set_value=dep_control["Set Chamber P"][index],
                                    value=row_to_array(
                                        dep_control,
                                        ["Read Chamber Pressure"],
                                        index,
                                    ),
                                    time=row_to_array(
                                        dep_control,
                                        ["Chamber pressure time"],
                                        index,
                                    ),
                                ),
                            ),
                        )
                    ],
                )
                growth_filename = f"{dep_control_run}.GrowthMovpeIKZ.archive.{filetype}"
                growth_archive = EntryArchive(
                    data=growth_data,
                    # m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    growth_archive.m_to_dict(),
                    archive.m_context,
                    growth_filename,
                    filetype,
                    logger,
                )

                # creating precursor objects
                component_objects = []
                precursor_quantities = [
                    "MO Precursor",
                    "Weight",
                    "Solvent",
                    "Volume",
                    "Molar conc",
                    "CAS",
                ]
                i = 0
                while True:
                    if all(
                        f"{key}{'' if i == 0 else '.' + str(i)}" in precursors.columns
                        for key in precursor_quantities
                    ):
                        solute_name = precursors.get(
                            f"MO Precursor{'' if i == 0 else '.' + str(i)}", ""
                        )[index]
                        solvent_name = (
                            precursors.get(
                                f"Solvent{'' if i == 0 else '.' + str(i)}",
                                0,
                            )[index]
                            if not None
                            else "unknown"
                        )
                        solution_filename = (
                            f"{solute_name}_{solvent_name}.Solution.archive.{filetype}"
                        )
                        solution_data = Solution(
                            solute=[
                                PureSubstanceComponent(
                                    mass=precursors.get(
                                        f"Weight{'' if i == 0 else '.' + str(i)}",
                                        0,
                                    )[index],
                                    name=solute_name,
                                    pure_substance=PureSubstanceSection(
                                        cas_number=precursors.get(
                                            f"CAS{'' if i == 0 else '.' + str(i)}",
                                            0,
                                        )[index],
                                    ),
                                ),
                            ],
                            solvent=[
                                LiquidComponent(
                                    name=solvent_name,
                                    volume=precursors.get(
                                        f"Volume{'' if i == 0 else '.' + str(i)}",
                                        0,
                                    )[index],
                                    pure_substance=PureSubstanceSection(
                                        cas_number=precursors.get(
                                            f"Solvent CAS{'' if i == 0 else '.' + str(i)}",
                                            0,
                                        )[index],
                                    ),
                                ),
                            ],
                        )
                        solution_archive = EntryArchive(
                            data=solution_data,
                            m_context=archive.m_context,
                            metadata=EntryMetadata(
                                upload_id=archive.m_context.upload_id
                            ),
                        )
                        create_archive(
                            solution_archive.m_to_dict(),
                            archive.m_context,
                            solution_filename,
                            filetype,
                            logger,
                        )
                        component_objects.append(
                            SystemComponentIKZ(
                                name=str(solute_name) + " in " + str(solvent_name),
                                system=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, solution_filename)}#data",
                                molar_concentration=precursors.get(
                                    f"Molar conc{'' if i == 0 else '.' + str(i)}", 0
                                )[index],
                            ),
                        )
                        i += 1
                    else:
                        break

                # create precursors preparation archive
                precursors_data = PrecursorsPreparationIKZ(
                    data_file=data_file_with_path,
                    lab_id=f"{precursors['Sample ID'][index]} precursor preparation",
                    name="Precursors",
                    description=f"{precursors['Weekday'][index]}. Sequential number: {precursors['number'][index]}.",
                    flow_titanium=precursors["Set flow Ti"][index],
                    flow_calcium=precursors["Set flow Ca"][index],
                    components=component_objects,
                )

                precursors_filename = f"{precursors['Sample ID'][index]}.PrecursorsPreparationIKZ.archive.{filetype}"
                precursors_archive = EntryArchive(
                    data=precursors_data,
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    precursors_archive.m_to_dict(),
                    archive.m_context,
                    precursors_filename,
                    filetype,
                    logger,
                )
                # create experiment archive
                experiment_filename = (
                    f"{dep_control_run}.ExperimentMovpeIKZ.archive.{filetype}"
                )
                experiment_archive = EntryArchive(
                    data=ExperimentMovpeIKZ(
                        lab_id=f"{dep_control_run} experiment",
                        datetime=dep_control["Date"][index],
                        precursors_preparation=PrecursorsPreparationIKZReference(
                            reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, precursors_filename)}#data",
                        ),
                        # growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
                        #     lab_id=dep_control["Constant Parameters ID"][index],
                        # ),
                        growth_run=GrowthMovpeIKZReference(
                            reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, growth_filename)}#data",
                        ),
                        # grown_sample=ThinFilmStackMovpeReference(
                        #     reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, sample_filename)}#data",
                        # ), # TODO to be LINKED INSIDE THE GROWTH STEP
                        # TODO to be LINKED INSIDE THE GROWTH STEP
                        # TODO to be LINKED INSIDE THE GROWTH STEP
                        # TODO to be LINKED INSIDE THE GROWTH STEP
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

                # !!! the following code checks if the experiment archive already exists and overwrites it

                # if len(matches["lab_id"]) == 0:
                #     experiment_archive = EntryArchive(
                #         data=ExperimentMovpeIKZ(
                #             lab_id=f"{dep_control_run} experiment",
                #             datetime=dep_control["Date"][index],
                #             precursors_preparation=PrecursorsPreparationIKZReference(
                #                 reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, precursors_filename)}#data",
                #             ),
                #             growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
                #                 lab_id=dep_control["Constant Parameters ID"][index],
                #             ),
                #             growth_run_deposition_control=growth_data,
                #             grown_sample=ThinFilmStackMovpeReference(
                #                 reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, sample_filename)}#data",
                #             ),
                #         ),
                #         m_context=archive.m_context,
                #         metadata=EntryMetadata(
                #             upload_id=archive.m_context.upload_id
                #         ),
                #     )
                #     create_archive(
                #         experiment_archive.m_to_dict(),
                #         archive.m_context,
                #         experiment_filename,
                #         filetype,
                #         logger,
                #     )
                # elif (
                #     len(matches["lab_id"]) > 0
                #     and matches["entry_name"][0] == experiment_filename
                # ):  # the experiment will be retrieved, extended, and overwritten
                #     from nomad.app.v1.routers.uploads import get_upload_with_read_access

                #     logger.warning(
                #         f"Overwritten existing experiment archive {matches['entry_name'][0]}."
                #     )

                #     experiment_context = ServerContext(
                #         get_upload_with_read_access(
                #             matches["upload_id"][0],
                #             User(
                #                 is_admin=True,
                #                 user_id=archive.metadata.main_author.user_id,
                #             ),
                #             include_others=True,
                #         )
                #     )  # Upload(upload_id=matches["upload_id"][0]))

                #     #     filename =
                #     with experiment_context.raw_file(
                #         experiment_filename, "r"
                #     ) as experiment_file:
                #         updated_experiment = yaml.safe_load(experiment_file)
                #         updated_experiment["data"][
                #             "precursors_preparation"
                #         ] = PrecursorsPreparationIKZReference(
                #             reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, precursors_filename)}#data",
                #         ).m_to_dict()
                #         updated_experiment["data"][
                #             "growth_run_deposition_control"
                #         ] = growth_data.m_to_dict()
                #         updated_experiment["data"]["grown_sample"] = ThinFilmStackMovpeReference(
                #             reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, sample_filename)}#data",
                #         ).m_to_dict()

                #     create_archive(
                #         updated_experiment,
                #         experiment_context,
                #         experiment_filename,
                #         filetype,
                #         logger,
                #         bypass_check=True,
                #     )

                deposition_control_list.append(
                    f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, experiment_filename)}#data"
                )

        # populate the raw file archive
        archive.data = RawFileMovpeDepositionControl(
            growth_run_deposition_control=deposition_control_list
        )
