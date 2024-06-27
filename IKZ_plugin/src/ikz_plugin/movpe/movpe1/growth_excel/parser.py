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
from nomad.datamodel.data import (
    EntryData,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
    PureSubstanceSection,
)
from nomad.metainfo import (
    Quantity,
    Section,
)
from nomad.parsing import MatchingParser
from nomad.units import ureg
from nomad.utils import hash
from nomad_material_processing import (
    SubstrateReference,
    ThinFilmReference,
)
from nomad_material_processing.vapor_deposition import (
    Pressure,
    Temperature,
    VolumetricFlowRate,
)
from nomad_material_processing.vapor_deposition.cvd import (
    FlashEvaporator,
    GasLine,
    Rotation,
)

from nomad.datamodel.datamodel import EntryArchive, EntryMetadata

from ikz_plugin.general.schema import (
    LiquidComponent,
    Solution,
)
from ikz_plugin.movpe.schema import (
    ChamberEnvironmentMovpe,
    ExperimentMovpeIKZ,
    FilamentTemperature,
    FlashSourceIKZ,
    GasSourceIKZ,
    GrowthMovpeIKZ,
    GrowthMovpeIKZReference,
    GrowthStepMovpe1IKZ,
    PrecursorsPreparationIKZ,
    PrecursorsPreparationIKZReference,
    SampleParametersMovpe,
    ShaftTemperature,
    SystemComponentIKZ,
    ThinFilmMovpeIKZ,
    ThinFilmStackMovpe,
    ThinFilmStackMovpeReference,
)
from ikz_plugin.utils import (
    clean_dataframe_headers,
    create_archive,
    get_hash_ref,
    row_timeseries,
)


class RawFileMovpeDepositionControl(EntryData):
    m_def = Section(
        a_eln=None,
        label="Raw File Growth Run Deposition Control",
    )
    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    growth_run_deposition_control = Quantity(
        type=ExperimentMovpeIKZ,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
        ),
        shape=["*"],
    )


class ParserMovpe1IKZ(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        from nomad.search import MetadataPagination, search

        filetype = "yaml"
        xlsx = pd.ExcelFile(mainfile)
        data_file = mainfile.split("/")[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        # Read the file without headers
        dep_control = pd.read_excel(
            xlsx, "Deposition Control", comment="#", header=None
        )
        precursors = pd.read_excel(xlsx, "Precursors", comment="#", header=None)

        dep_control = clean_dataframe_headers(dep_control)

        precursors = clean_dataframe_headers(precursors)

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
                    data=ThinFilmMovpeIKZ(
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

                # parsing arrays from excel file
                uniform_setval = pd.Series(
                    [
                        dep_control["Set of argon uniform gas"].loc[index]
                        * ureg("cm ** 3 / minute").to("meter ** 3 / second").magnitude
                    ]
                )

                fil_temp_setval = pd.Series([dep_control["Set Fil T"].loc[index]])
                fil_temp_time, fil_temp_val = row_timeseries(
                    dep_control, "Fil time", "Read Fil T", index
                )
                fil_temp_time = fil_temp_time * ureg("minute").to("second").magnitude

                shaft_temp_setval = pd.Series([dep_control["Set Shaft T"].loc[index]])
                shaft_temp_time, shaft_temp_val = row_timeseries(
                    dep_control, "Shaft time", "Read Shaft T", index
                )
                shaft_temp_time = (
                    shaft_temp_time * ureg("minute").to("second").magnitude
                )

                pressure_setval = pd.Series(
                    [
                        (
                            dep_control["Set Chamber P"].loc[index]
                            if "Set Chamber P" in dep_control.columns
                            else None
                        )
                    ]
                )
                pressure_time, pressure_val = row_timeseries(
                    dep_control, "Chamber pressure time", "Read Chamber Pressure", index
                )
                pressure_time = pressure_time * ureg("minute").to("second").magnitude

                throttle_time, throttle_val = row_timeseries(
                    dep_control, "TV time", "Read throttle valve", index
                )

                rot_setval = pd.Series(
                    [
                        (
                            dep_control["Set Rotation S"].loc[index]
                            if "Set Rotation S" in dep_control.columns
                            else None
                        )
                    ]
                )
                rot_time, rot_val = row_timeseries(
                    dep_control, "rot time", "Read rotation", index
                )
                rot_time = rot_time * ureg("minute").to("second").magnitude

                fe1_pressure_time, fe1_pressure_val = row_timeseries(
                    dep_control, "BP FE1 time", "BP FE1", index
                )
                fe1_pressure_time = (
                    fe1_pressure_time * ureg("minute").to("second").magnitude
                )

                fe1_temp_setval = pd.Series(
                    [
                        (
                            dep_control["Set FE1 Temp"].loc[index]
                            if "Set FE1 Temp" in dep_control.columns
                            else None
                        )
                    ]
                )

                fe1_ar_push_setval = pd.Series(
                    [
                        (
                            dep_control["Set Ar Push 1"].loc[index]
                            if "Set Ar Push 1" in dep_control.columns
                            else None
                        )
                    ]
                )

                fe1_ar_purge_setval = pd.Series(
                    [
                        (
                            dep_control["Set Ar Purge 1"].loc[index]
                            if "Set Ar Purge 1" in dep_control.columns
                            else None
                        )
                    ]
                )

                fe2_pressure_time, fe2_pressure_val = row_timeseries(
                    dep_control, "BP FE2 time", "BP FE2", index
                )
                fe2_pressure_time = (
                    fe2_pressure_time * ureg("minute").to("second").magnitude
                )

                fe2_temp_setval = pd.Series(
                    [
                        (
                            dep_control["Set FE2 Temp"].loc[index]
                            if "Set FE2 Temp" in dep_control.columns
                            else None
                        )
                    ]
                )

                fe2_ar_push_setval = pd.Series(
                    [
                        (
                            dep_control["Set Ar Push 2"].loc[index]
                            if "Set Ar Push 2" in dep_control.columns
                            else None
                        )
                    ]
                )

                fe2_ar_purge_setval = pd.Series(
                    [
                        (
                            dep_control["Set Ar Purge 2"].loc[index]
                            if "Set Ar Purge 2" in dep_control.columns
                            else None
                        )
                    ]
                )

                gas_temp_time, gas_temp_val = row_timeseries(
                    dep_control, "Oxygen time", "Read Oxygen T", index
                )
                gas_temp_time = gas_temp_time * ureg("minute").to("second").magnitude

                gas_mfc_setval = pd.Series(
                    [
                        (
                            dep_control["Set of Oxygen uniform gas"].loc[index]
                            if "Set of Oxygen uniform gas" in dep_control.columns
                            else None
                        )
                    ]
                )
                growth_description = (
                    str(
                        dep_control["Weekday"].loc[index]
                        if "Weekday" in dep_control.columns
                        else None
                    )
                    + ". Sequential number: "
                    + str(dep_control["number"].loc[index])
                    + ". "
                    + str(dep_control["Comment"].loc[index])
                )

                # creating GrowthMovpeIKZ archive
                growth_data = GrowthMovpeIKZ(
                    data_file=data_file_with_path,
                    name="Growth MOVPE 1",
                    lab_id=dep_control_run,
                    description=growth_description,
                    datetime=(
                        dep_control["Date"].loc[index]
                        if "Date" in dep_control.columns
                        else None
                    ),
                    steps=[
                        GrowthStepMovpe1IKZ(
                            name="Deposition",
                            duration=(
                                dep_control["Duration"].loc[index]
                                if "Duration" in dep_control.columns
                                else None
                            ),
                            environment=ChamberEnvironmentMovpe(
                                pressure=Pressure(
                                    set_time=pd.Series([0]),
                                    set_value=pressure_setval,
                                    value=pressure_val,
                                    time=pressure_time,
                                ),
                                throttle_valve=Pressure(
                                    value=throttle_val,
                                    time=throttle_time,
                                ),
                                rotation=Rotation(
                                    set_time=pd.Series([0]),
                                    set_value=rot_setval,
                                    value=rot_val,
                                    time=rot_time,
                                ),
                                uniform_gas_flow_rate=VolumetricFlowRate(
                                    set_time=pd.Series([0]),
                                    set_value=uniform_setval,
                                ),
                            ),
                            sample_parameters=[
                                SampleParametersMovpe(
                                    layer=ThinFilmReference(
                                        reference=f"{get_hash_ref(archive.m_context.upload_id, layer_filename)}",
                                    ),
                                    substrate=ThinFilmStackMovpeReference(
                                        reference=f"{get_hash_ref(archive.m_context.upload_id, grown_sample_filename)}",
                                    ),
                                    shaft_temperature=ShaftTemperature(
                                        set_time=pd.Series([0]),
                                        set_value=shaft_temp_setval,
                                        value=shaft_temp_val,
                                        time=shaft_temp_time,
                                    ),
                                    filament_temperature=FilamentTemperature(
                                        set_time=pd.Series([0]),
                                        set_value=fil_temp_setval,
                                        value=fil_temp_val,
                                        time=fil_temp_time,
                                    ),
                                )
                            ],
                            sources=[
                                FlashSourceIKZ(
                                    name="Flash Evaporator 1",
                                    vapor_source=FlashEvaporator(
                                        pressure=Pressure(
                                            value=fe1_pressure_val,
                                            time=fe1_pressure_time,
                                        ),
                                        temperature=Temperature(
                                            set_time=pd.Series([0]),
                                            set_value=fe1_temp_setval,
                                        ),
                                        carrier_gas=PubChemPureSubstanceSection(
                                            name="Argon",
                                        ),
                                        carrier_push_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe1_ar_push_setval,
                                        ),
                                        carrier_purge_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe1_ar_purge_setval,
                                        ),
                                    ),
                                ),
                                FlashSourceIKZ(
                                    name="Flash Evaporator 2",
                                    vapor_source=FlashEvaporator(
                                        pressure=Pressure(
                                            value=fe2_pressure_val,
                                            time=fe2_pressure_time,
                                        ),
                                        temperature=Temperature(
                                            set_time=pd.Series([0]),
                                            set_value=fe2_temp_setval,
                                        ),
                                        carrier_gas=PubChemPureSubstanceSection(
                                            name="Argon",
                                        ),
                                        carrier_push_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe2_ar_push_setval,
                                        ),
                                        carrier_purge_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe2_ar_purge_setval,
                                        ),
                                    ),
                                ),
                                GasSourceIKZ(
                                    name="Oxygen uniform gas ",
                                    vapor_source=GasLine(
                                        temperature=Temperature(
                                            value=gas_temp_val,
                                            time=gas_temp_time,
                                        ),
                                        total_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=gas_mfc_setval,
                                        ),
                                    ),
                                ),
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
                                system=get_hash_ref(
                                    archive.m_context.upload_id, solution_filename
                                ),
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
                            reference=get_hash_ref(
                                archive.m_context.upload_id, precursors_filename
                            ),
                        ),
                        # growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
                        #     lab_id=dep_control["Constant Parameters ID"].loc[index],
                        # ),
                        growth_run=GrowthMovpeIKZReference(
                            reference=get_hash_ref(
                                archive.m_context.upload_id, growth_filename
                            ),
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
                    get_hash_ref(archive.m_context.upload_id, experiment_filename)
                )

        # populate the raw file archive
        archive.data = RawFileMovpeDepositionControl(
            name=data_file, growth_run_deposition_control=deposition_control_list
        )
