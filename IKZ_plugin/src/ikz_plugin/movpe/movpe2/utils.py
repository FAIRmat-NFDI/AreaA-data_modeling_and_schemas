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
from typing import Dict, List
import yaml
import json
import math

from nomad.datamodel.context import ClientContext

from nomad.datamodel import EntryArchive
from nomad.metainfo import MSection, Quantity, Section
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from nomad.units import ureg

from nomad.datamodel.metainfo.basesections import (
    SystemComponent,
    CompositeSystemReference,
)

from ikz_plugin import IKZMOVPE2Category
from nomad.search import search

# from nomad_material_processing.utils import create_archive as create_archive_ref
from nomad_material_processing import (
    SubstrateReference,
)
from nomad_material_processing.chemical_vapor_deposition import (
    BubblerEvaporator,
    CVDSource,
)

from ikz_plugin.movpe import (
    BubblerSourceIKZ,
    GasSourceIKZ,
    CVDVaporRateMovpeIKZ,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata


def get_reference(upload_id, entry_id):
    return f"../uploads/{upload_id}/archive/{entry_id}"


def get_entry_id_from_file_name(filename, upload_id):
    from nomad.utils import hash

    return hash(upload_id, filename)


def nan_equal(a, b):
    """
    Compare two values with NaN values.
    """
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    elif isinstance(a, dict) and isinstance(b, dict):
        return dict_nan_equal(a, b)
    elif isinstance(a, list) and isinstance(b, list):
        return list_nan_equal(a, b)
    else:
        return a == b


def list_nan_equal(list1, list2):
    """
    Compare two lists with NaN values.
    """
    if len(list1) != len(list2):
        return False
    for a, b in zip(list1, list2):
        if not nan_equal(a, b):
            return False
    return True


def dict_nan_equal(dict1, dict2):
    """
    Compare two dictionaries with NaN values.
    """
    if set(dict1.keys()) != set(dict2.keys()):
        return False
    for key in dict1:
        if not nan_equal(dict1[key], dict2[key]):
            return False
    return True


def create_archive(
    entry_dict, context, filename, file_type, logger, *, overwrite: bool = False
):
    if isinstance(context, ClientContext):
        return None
    if context.raw_path_exists(filename):
        with context.raw_file(filename, "r") as file:
            existing_dict = yaml.safe_load(file)
    if context.raw_path_exists(filename) and not dict_nan_equal(
        existing_dict, entry_dict
    ):
        logger.error(
            f"{filename} archive file already exists. "
            f"You are trying to overwrite it with a different content. "
            f"To do so, remove the existing archive and click reprocess again."
        )
    if (
        not context.raw_path_exists(filename)
        or existing_dict == entry_dict
        or overwrite
    ):
        with context.raw_file(filename, "w") as newfile:
            if file_type == "json":
                json.dump(entry_dict, newfile)
            elif file_type == "yaml":
                yaml.dump(entry_dict, newfile)
        context.upload.process_updated_raw_file(filename, allow_modify=True)

    return get_reference(
        context.upload_id, get_entry_id_from_file_name(filename, context.upload_id)
    )

    # !! useful to fetch the upload_id from another upload.
    # experiment_context = ServerContext(
    #         get_upload_with_read_access(
    #             matches["upload_id"][0],
    #             User(
    #                 is_admin=True,
    #                 user_id=current_parse_archive.metadata.main_author.user_id,
    #             ),
    #             include_others=True,
    #         )
    #     )  # Upload(upload_id=matches["upload_id"][0]))


# def create_archive(
#     entry_dict, context, file_name, file_type, logger, *, bypass_check: bool = False
# ):
#     import yaml
#     import json

#     if not context.raw_path_exists(file_name) or bypass_check:
#         with context.raw_file(file_name, "w") as outfile:
#             if file_type == "json":
#                 json.dump(entry_dict, outfile)
#             elif file_type == "yaml":
#                 yaml.dump(entry_dict, outfile)
#         context.upload.process_updated_raw_file(file_name, allow_modify=True)
#     else:
#         logger.error(
#             f"{file_name} archive file already exists."
#             f"If you intend to reprocess the older archive file, remove the existing one and run reprocessing again."
#         )


def fetch_substrate(archive, sample_id, substrate_id, logger):
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
        logger.warn(
            f"Substrate entry [{substrate_id}] was not found, upload and reprocess to reference it in ThinFilmStack entry [{sample_id}]"
        )
        return None
    if len(search_result.data) > 1:
        logger.warn(
            f"Found {search_result.pagination.total} entries with lab_id: "
            f'"{substrate_id}". Will use the first one found.'
        )
        return None
    if len(search_result.data) >= 1:
        substrate_reference_str = f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
        return substrate_reference_str


def populate_sources(line_number, growth_run_file: pd.DataFrame):
    """
    Populate the Bubbler object from the growth run file
    """
    sources = []
    bubbler_quantities = [
        "Bubbler Temp",
        "Bubbler Pressure",
        "Bubbler Partial Pressure",
        "Bubbler Dilution",
        "Source",
        "Inject",
        "Bubbler MFC",
        "Bubbler Molar Flux",
        "Bubbler Material",
    ]
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in growth_run_file.columns
            for key in bubbler_quantities
        ):
            sources.append(
                BubblerSourceIKZ(
                    name=growth_run_file.get(
                        f"Bubbler Material{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                    material=CompositeSystemReference(
                        name=growth_run_file.get(
                            f"Bubbler Material{'' if i == 0 else '.' + str(i)}", ""
                        )[line_number],
                    ),
                    vapor_source=BubblerEvaporator(
                        temperature=growth_run_file.get(
                            f"Bubbler Temp{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        pressure=growth_run_file.get(
                            f"Bubbler Pressure{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        partial_pressure=growth_run_file.get(
                            f"Bubbler Partial Pressure{'' if i == 0 else '.' + str(i)}",
                            0,
                        )[line_number],
                        dilution=growth_run_file.get(
                            f"Bubbler Dilution{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        source=growth_run_file.get(
                            f"Source{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        inject=growth_run_file.get(
                            f"Inject{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                    ),
                    vapor_rate=CVDVaporRateMovpeIKZ(
                        measurement_type="Mass Flow Controller",
                        mass_flow_controller=growth_run_file.get(
                            f"Bubbler MFC{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        rate=[
                            growth_run_file.get(
                                f"Bubbler Molar Flux{'' if i == 0 else '.' + str(i)}", 0
                            )[line_number]
                            * ureg("mol / minute").to("mol / second").magnitude
                        ],
                        process_time=[0],
                    ),
                )
            )

            i += 1
        else:
            break
    return sources


def populate_gas_source(line_number, growth_run_file: pd.DataFrame):
    """
    Populate the GasSource object from the growth run file
    """
    gas_sources = []
    gas_source_quantities = [
        "Gas Material",
        "Gas MFC",
        "Gas Molar Flux",
    ]
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in growth_run_file.columns
            for key in gas_source_quantities
        ):
            gas_sources.append(
                GasSourceIKZ(
                    name=growth_run_file.get(
                        f"Gas Material{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                    material=CompositeSystemReference(
                        name=growth_run_file.get(
                            f"Gas Material{'' if i == 0 else '.' + str(i)}", ""
                        )[line_number],
                    ),
                    vapor_rate=CVDVaporRateMovpeIKZ(
                        measurement_type="Mass Flow Controller",
                        mass_flow_controller=growth_run_file.get(
                            f"Gas MFC{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        rate=[
                            growth_run_file.get(
                                f"Gas Molar Flux{'' if i == 0 else '.' + str(i)}", 0
                            )[line_number]
                            * ureg("mol / minute").to("mol / second").magnitude
                        ],
                        process_time=[0],
                    ),
                )
            )
            i += 1
        else:
            break
    return gas_sources
