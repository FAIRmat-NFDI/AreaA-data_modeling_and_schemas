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

from ikz_plugin import (
    IKZMOVPE1Category,
    Solution,
    LiquidComponent,
)
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
    ThinFilmMovpe,
    SystemComponentIKZ,
    SampleParametersMovpe,
    ChamberEnvironmentMovpe,
    FilamentTemperature,
    FlashEvaporator1Pressure,
    FlashEvaporator2Pressure,
    OxygenTemperature,
    ShaftTemperature,
    FilamentTemperature,
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
        # Read the file without headers
        dep_control = pd.read_excel(
            xlsx, "Deposition Control", comment="#", header=None
        )
        precursors = pd.read_excel(xlsx, "Precursors", comment="#", header=None)

        # # Strip and rename the columns
        # dep_control.columns = [
        #     re.sub(r"\s+", " ", str(col).strip()) for col in dep_control.iloc[0]
        # ]
        # precursors.columns = [
        #     re.sub(r"\s+", " ", str(col).strip()) for col in precursors.iloc[0]
        # ]

        # Create a dictionary to keep track of the count of each column name
        column_counts = {}
        # Create a list to store the new column names
        new_columns = []
        # Iterate over the columns
        for col in dep_control.iloc[0]:
            # Clean up the column name
            col = re.sub(r"\s+", " ", str(col).strip())
            # If the column name is in the dictionary, increment the count
            if col in column_counts:
                column_counts[col] += 1
            # Otherwise, add the column name to the dictionary with a count of 1
            else:
                column_counts[col] = 1
            # If the count is greater than 1, append it to the column name
            if column_counts[col] > 1:
                col = f"{col}.{column_counts[col] - 1}"
            # Add the column name to the list of new column names
            new_columns.append(col)
        # Assign the new column names to the DataFrame
        dep_control.columns = new_columns

        # Create a dictionary to keep track of the count of each column name
        column_counts = {}
        # Create a list to store the new column names
        new_columns = []
        # Iterate over the columns
        for col in precursors.iloc[0]:
            # Clean up the column name
            col = re.sub(r"\s+", " ", str(col).strip())
            # If the column name is in the dictionary, increment the count
            if col in column_counts:
                column_counts[col] += 1
            # Otherwise, add the column name to the dictionary with a count of 1
            else:
                column_counts[col] = 1
            # If the count is greater than 1, append it to the column name
            if column_counts[col] > 1:
                col = f"{col}.{column_counts[col] - 1}"
            # Add the column name to the list of new column names
            new_columns.append(col)
        # Assign the new column names to the DataFrame
        precursors.columns = new_columns

        # Remove the first row (which contains the original headers)
        dep_control = dep_control.iloc[1:]
        precursors = precursors.iloc[1:]
        # Reset the index
        dep_control = dep_control.reset_index(drop=True)
        precursors = precursors.reset_index(drop=True)

        deposition_control_list = []

        if not len(dep_control["Sample ID"]) == len(precursors["Sample ID"]):
            logger.error(
                f"Excel sheets mismatch: "
                f"'Deposition Control' has {len(dep_control['Sample ID'])} rows "
                f"and 'Precursors' has {len(precursors['Sample ID'])} rows. "
                f"Please check the file and try again."
            )

        for index, dep_control_run in enumerate(dep_control["Sample ID"]):
            assert dep_control_run == precursors["Sample ID"].loc[index], (
                f"Not matching Sample ID at line {index} in "
                f"'deposition control' [{dep_control_run}] "
                f"and 'precursors' [{precursors['Sample ID'].loc[index]}] sheets."
                f"Please check the files and try again."
            )

            # check if experiment archive exists already
            search_experiments = search(
                owner="user",
                query={
                    "results.eln.sections:any": ["ExperimentMovpeIKZ"],
                    "results.eln.methods:any": ["MOVPE 1 experiment"],
                    "upload_id:any": [archive.m_context.upload_id],
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
                # creating ThinFiln and ThinFilmStack archives
                layer_filename = (
                    f"{dep_control_run}_{index}.ThinFilm.archive.{filetype}"
                )
                layer_archive = EntryArchive(
                    data=ThinFilmMovpe(
                        name=dep_control_run + "layer",
                        lab_id=dep_control_run + "layer",
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
                grown_sample_filename = (
                    f"{dep_control_run}.ThinFilmStackMovpe.archive.{filetype}"
                )
                grown_sample_archive = EntryArchive(
                    data=ThinFilmStackMovpe(
                        name=dep_control_run + "stack",
                        lab_id=dep_control_run,
                        substrate=SubstrateReference(
                            lab_id=dep_control["Substrate ID"].loc[index],
                        ),
                        layers=[
                            ThinFilmReference(
                                reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, layer_filename)}#data"
                            )
                        ],
                    ),
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
                throttle_valves = create_timeseries_objects(
                    dep_control, ["Oxygen time", "Oxygen T"], ThrottleValve, index
                )

                # creating GrowthMovpeIKZ archive
                growth_data = GrowthMovpeIKZ(
                    data_file=data_file_with_path,
                    name="Growth MOVPE 1",
                    lab_id=dep_control_run,
                    description=f"{dep_control['Weekday'].loc[index]}. Sequential number: {dep_control['number'].loc[index]}. {dep_control['Comment'].loc[index]}",
                    datetime=dep_control["Date"].loc[index],
                    steps=[
                        GrowthStepMovpe1IKZ(
                            name="Deposition",
                            duration=dep_control["Duration"].loc[index],
                            flash_evaporator1_pressure=flash_evaporator1_pressures,
                            flash_evaporator2_pressure=flash_evaporator2_pressures,
                            oxygen_temperature=oxygen_temperatures,
                            throttle_valve=throttle_valves,
                            environment=ChamberEnvironmentMovpe(
                                pressure=Pressure(
                                    set_value=dep_control["Set Chamber P"].loc[index],
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
                                    set_value=dep_control["Set Chamber P"].loc[index],
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
                            sample_parameters=[
                                SampleParametersMovpe(
                                    layer=ThinFilmReference(
                                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, layer_filename)}#data",
                                    ),
                                    substrate=ThinFilmStackMovpeReference(
                                        reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, grown_sample_filename)}#data",
                                    ),
                                    shaft_temperature=ShaftTemperature(
                                        set_value=dep_control["Set Shaft T"].loc[index],
                                        value=row_to_array(
                                            dep_control,
                                            ["Read Shaft T"],
                                            index,
                                        ),
                                        time=row_to_array(
                                            dep_control,
                                            ["Shaft time"],
                                            index,
                                        ),
                                    ),
                                    filament_temperature=FilamentTemperature(
                                        set_value=dep_control["Set Fil T"].loc[index],
                                        value=row_to_array(
                                            dep_control,
                                            ["Read Fil T"],
                                            index,
                                        ),
                                        time=row_to_array(
                                            dep_control,
                                            ["Fil time"],
                                            index,
                                        ),
                                    ),
                                    # distance_to_source=[
                                    #     (
                                    #         growth_run_file["Distance of Showerhead"][
                                    #             index
                                    #         ]
                                    #     )
                                    #     * ureg("millimeter").to("meter").magnitude
                                    # ],
                                    # temperature=SubstrateTemperatureMovpe(
                                    #     temperature=[
                                    #         growth_run_file["T LayTec"].loc[index]
                                    #     ],
                                    #     process_time=[
                                    #         0
                                    #     ],  # [growth_run_file["Duration"].loc[index]],
                                    #     temperature_shaft=growth_run_file["T Shaft"][
                                    #         index
                                    #     ],
                                    #     temperature_filament=growth_run_file[
                                    #         "T Filament"
                                    #     ].loc[index],
                                    # ),
                                )
                            ],
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
                        ).loc[index]
                        solvent_name = (
                            precursors.get(
                                f"Solvent{'' if i == 0 else '.' + str(i)}",
                                0,
                            ).loc[index]
                            if not None
                            else "unknown"
                        )
                        solute_mass = precursors.get(
                            f"Weight{'' if i == 0 else '.' + str(i)}",
                            0,
                        ).loc[index]
                        solvent_volume = precursors.get(
                            f"Volume{'' if i == 0 else '.' + str(i)}",
                            0,
                        ).loc[index]
                        solution_filename = f"{solute_name}-mass{solute_mass}_{solvent_name}-vol{solvent_volume}.Solution.archive.{filetype}"
                        solution_data = Solution(
                            name=f"{solute_name} in {solvent_name}",
                            solute=[
                                PureSubstanceComponent(
                                    mass=solute_mass,
                                    name=solute_name,
                                    pure_substance=PureSubstanceSection(
                                        cas_number=precursors.get(
                                            f"CAS{'' if i == 0 else '.' + str(i)}",
                                            0,
                                        ).loc[index],
                                    ),
                                ),
                            ],
                            solvent=[
                                LiquidComponent(
                                    name=solvent_name,
                                    volume=solvent_volume,
                                    pure_substance=PureSubstanceSection(
                                        cas_number=precursors.get(
                                            f"Solvent CAS{'' if i == 0 else '.' + str(i)}",
                                            0,
                                        ).loc[index],
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
                                ).loc[index],
                            ),
                        )
                        i += 1
                    else:
                        break

                # create precursors preparation archive
                precursors_data = PrecursorsPreparationIKZ(
                    data_file=data_file_with_path,
                    lab_id=f"{precursors['Sample ID'].loc[index]} precursor preparation",
                    name="Precursors",
                    description=f"{precursors['Weekday'].loc[index]}. Sequential number: {precursors['number'].loc[index]}.",
                    flow_titanium=precursors["Set flow Ti"].loc[index],
                    flow_calcium=precursors["Set flow Ca"].loc[index],
                    components=component_objects,
                )

                precursors_filename = f"{precursors['Sample ID'].loc[index]}.PrecursorsPreparationIKZ.archive.{filetype}"
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
                        name=f"{dep_control_run} experiment",
                        method="MOVPE 1 experiment",
                        lab_id=f"{dep_control_run} experiment",
                        datetime=dep_control["Date"].loc[index],
                        precursors_preparation=PrecursorsPreparationIKZReference(
                            reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, precursors_filename)}#data",
                        ),
                        # growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
                        #     lab_id=dep_control["Constant Parameters ID"].loc[index],
                        # ),
                        growth_run=GrowthMovpeIKZReference(
                            reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, growth_filename)}#data",
                        ),
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
                #             datetime=dep_control["Date"].loc[index],
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
            name=data_file, growth_run_deposition_control=deposition_control_list
        )
