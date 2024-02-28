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
from ikz_plugin import IKZMOVPE1Category
from ikz_plugin.movpe import (
    ExperimentMovpe1IKZ,
    GrowthMovpe1IKZConstantParametersReference,
    GrowthMovpe1IKZDepositionControl,
    PrecursorsPreparationMovpe1IKZ,
    PrecursorsPreparationMovpe1IKZReference,
    PureSubstanceComponentMovpe1IKZ,
    PubChemPureSubstanceSectionMovpe1,
    ThinFilmStackMovpeReference,
    ThinFilmStackMovpe,
    ChamberPressure,
    Rotation,
    FilamentTemperature,
    FlashEvaporator1Pressure,
    FlashEvaporator2Pressure,
    OxygenTemperature,
    ShaftTemperature,
    ThrottleValve,
    RawFileMovpeDepositionControl,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata

# from nomad.parsing.tabular import create_archive
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


class ParserMovpe1DepositionControlIKZ(MatchingParser):
    def __init__(self):
        super().__init__(
            name="MOVPE 1 Deposition Control IKZ",
            code_name="MOVPE 1 Deposition Control IKZ",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, current_parse_archive: EntryArchive, logger) -> None:
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
                "Number of rows in 'deposition control' and 'precursors' Excel sheets are not equal. Please check the files and try again."
            )

        def create_objects(dataframe: pd.DataFrame, quantities, MetainfoClass, index):
            objects = []
            i = 0
            while True:
                if all(
                    f"{key}{'' if i == 0 else '.' + str(i)}" in dataframe.columns
                    for key in quantities
                ):
                    objects.append(
                        MetainfoClass(
                            time=dataframe.get(
                                f"{quantities[0]}{'' if i == 0 else '.' + str(i)}", ""
                            )[index],
                            value=dataframe.get(
                                f"{quantities[1]}{'' if i == 0 else '.' + str(i)}", 0
                            )[index],
                        )
                    )
                    i += 1
                else:
                    break
            return objects

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
                    "results.eln.sections:any": ["ExperimentMovpe1IKZ"],
                },
                pagination=MetadataPagination(page_size=10000),
                user_id=current_parse_archive.metadata.main_author.user_id,
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
                        f"One entry with lab_id {set(matches['lab_id'])} and entry_id {set(matches['entry_id'])} already exists. Please check it."
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
                    data=ThinFilmStackMovpe(lab_id=dep_control_run),
                    m_context=current_parse_archive.m_context,
                    metadata=EntryMetadata(
                        upload_id=current_parse_archive.m_context.upload_id
                    ),
                )
                create_archive(
                    sample_archive.m_to_dict(),
                    current_parse_archive.m_context,
                    sample_filename,
                    filetype,
                    logger,
                )
                # create deposition control objects
                chamber_pressures = create_objects(
                    dep_control,
                    ["reactor time", "Pressure"],
                    ChamberPressure,
                    index,
                )
                rotations = create_objects(
                    dep_control, ["rot time", "rotation"], Rotation, index
                )
                filament_temperatures = create_objects(
                    dep_control, ["Fil time", "Fil T"], FilamentTemperature, index
                )
                flash_evaporator1_pressures = create_objects(
                    dep_control,
                    ["BP FE1 time", "BP FE1"],
                    FlashEvaporator1Pressure,
                    index,
                )
                flash_evaporator2_pressures = create_objects(
                    dep_control,
                    ["BP FE2 time", "BP FE2"],
                    FlashEvaporator2Pressure,
                    index,
                )
                oxygen_temperatures = create_objects(
                    dep_control,
                    ["Oxygen time", "Oxygen T"],
                    OxygenTemperature,
                    index,
                )
                shaft_temperatures = create_objects(
                    dep_control,
                    ["Oxygen time", "Oxygen T"],
                    ShaftTemperature,
                    index,
                )
                throttle_valves = create_objects(
                    dep_control, ["Oxygen time", "Oxygen T"], ThrottleValve, index
                )
                # creating deposition control object
                dep_control_data = GrowthMovpe1IKZDepositionControl(
                    data_file=data_file_with_path,
                    description=f"{dep_control['Weekday'][index]}. Sequential number: {dep_control['number'][index]}. {dep_control['Comment'][index]}",
                    datetime=dep_control["Date"][index],
                    # lab_id=f"{dep_control['Sample ID'][index]} growth run deposition control",
                    duration=dep_control["Duration"][index],
                    chamber_pressure=chamber_pressures,
                    filament_temperature=filament_temperatures,
                    flash_evaporator1_pressure=flash_evaporator1_pressures,
                    flash_evaporator2_pressure=flash_evaporator2_pressures,
                    oxygen_temperature=oxygen_temperatures,
                    rotation=rotations,
                    shaft_temperature=shaft_temperatures,
                    throttle_valve=throttle_valves,
                )
                # creating precursor objects
                precursor_objects = []
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
                        precursor_objects.append(
                            PureSubstanceComponentMovpe1IKZ(
                                name=precursors.get(
                                    f"MO Precursor{'' if i == 0 else '.' + str(i)}",
                                    "",
                                )[index],
                                mass=precursors.get(
                                    f"Weight{'' if i == 0 else '.' + str(i)}", 0
                                )[index],
                                solvent=precursors.get(
                                    f"Solvent{'' if i == 0 else '.' + str(i)}", 0
                                )[index],
                                volume=precursors.get(
                                    f"Volume{'' if i == 0 else '.' + str(i)}", 0
                                )[index],
                                molar_concentration=precursors.get(
                                    f"Molar conc{'' if i == 0 else '.' + str(i)}", 0
                                )[index],
                                pure_substance=PubChemPureSubstanceSectionMovpe1(
                                    cas_number=precursors.get(
                                        f"CAS{'' if i == 0 else '.' + str(i)}", 0
                                    )[index],
                                ),
                            )
                        )
                        i += 1
                    else:
                        break
                # create precursors preparation archive
                precursors_filename = f"{precursors['Sample ID'][index]}.PrecursorsPreparationMovpe1IKZ.archive.{filetype}"
                precursors_archive = EntryArchive(
                    data=PrecursorsPreparationMovpe1IKZ(
                        data_file=data_file_with_path,
                        lab_id=f"{precursors['Sample ID'][index]} precursor preparation",
                        name=f"{precursors['Sample ID'][index]} precursors preparation ",
                        description=f"{precursors['Weekday'][index]}. Sequential number: {precursors['number'][index]}.",
                        flow_titanium=precursors["Set flow Ti"][index],
                        flow_calcium=precursors["Set flow Ca"][index],
                        precursors=precursor_objects,
                    ),
                    m_context=current_parse_archive.m_context,
                    metadata=EntryMetadata(
                        upload_id=current_parse_archive.m_context.upload_id
                    ),
                )
                create_archive(
                    precursors_archive.m_to_dict(),
                    current_parse_archive.m_context,
                    precursors_filename,
                    filetype,
                    logger,
                )
                # create experiment archive
                experiment_filename = (
                    f"{dep_control_run}.ExperimentMovpe1IKZ.archive.{filetype}"
                )
                experiment_archive = EntryArchive(
                    data=ExperimentMovpe1IKZ(
                        lab_id=f"{dep_control_run} experiment",
                        datetime=dep_control["Date"][index],
                        precursors_preparation=PrecursorsPreparationMovpe1IKZReference(
                            reference=f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.m_context.upload_id, precursors_filename)}#data",
                        ),
                        growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
                            lab_id=dep_control["Constant Parameters ID"][index],
                        ),
                        growth_run_deposition_control=dep_control_data,
                        grown_sample=ThinFilmStackMovpeReference(
                            reference=f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.m_context.upload_id, sample_filename)}#data",
                        ),
                    ),
                    m_context=current_parse_archive.m_context,
                    metadata=EntryMetadata(
                        upload_id=current_parse_archive.m_context.upload_id
                    ),
                )
                create_archive(
                    experiment_archive.m_to_dict(),
                    current_parse_archive.m_context,
                    experiment_filename,
                    filetype,
                    logger,
                )

                # !!! the following code checks if the experiment archive already exists and overwrites it

                # if len(matches["lab_id"]) == 0:
                #     experiment_archive = EntryArchive(
                #         data=ExperimentMovpe1IKZ(
                #             lab_id=f"{dep_control_run} experiment",
                #             datetime=dep_control["Date"][index],
                #             precursors_preparation=PrecursorsPreparationMovpe1IKZReference(
                #                 reference=f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.m_context.upload_id, precursors_filename)}#data",
                #             ),
                #             growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
                #                 lab_id=dep_control["Constant Parameters ID"][index],
                #             ),
                #             growth_run_deposition_control=dep_control_data,
                #             grown_sample=ThinFilmStackMovpeReference(
                #                 reference=f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.m_context.upload_id, sample_filename)}#data",
                #             ),
                #         ),
                #         m_context=current_parse_archive.m_context,
                #         metadata=EntryMetadata(
                #             upload_id=current_parse_archive.m_context.upload_id
                #         ),
                #     )
                #     create_archive(
                #         experiment_archive.m_to_dict(),
                #         current_parse_archive.m_context,
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
                #                 user_id=current_parse_archive.metadata.main_author.user_id,
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
                #         ] = PrecursorsPreparationMovpe1IKZReference(
                #             reference=f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.m_context.upload_id, precursors_filename)}#data",
                #         ).m_to_dict()
                #         updated_experiment["data"][
                #             "growth_run_deposition_control"
                #         ] = dep_control_data.m_to_dict()
                #         updated_experiment["data"]["grown_sample"] = ThinFilmStackMovpeReference(
                #             reference=f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.m_context.upload_id, sample_filename)}#data",
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
                    f"../uploads/{current_parse_archive.m_context.upload_id}/archive/{hash(current_parse_archive.metadata.upload_id, experiment_filename)}#data"
                )

        # populate the raw file archive
        current_parse_archive.data = RawFileMovpeDepositionControl(
            growth_run_deposition_control=deposition_control_list
        )
