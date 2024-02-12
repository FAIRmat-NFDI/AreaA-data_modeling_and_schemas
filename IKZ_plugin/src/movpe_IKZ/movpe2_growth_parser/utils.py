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

from nomad.datamodel.metainfo.basesections import (
    SystemComponent,
    CompositeSystemReference,
)

from basesections_IKZ import IKZMOVPE2Category
from nomad.search import search

# from nomad_material_processing.utils import create_archive as create_archive_ref
from nomad_material_processing import (
    SubstrateReference,
)
from nomad_material_processing.chemical_vapor_deposition import (
    CVDBubbler,
    CVDVaporRate,
    CVDSource,
    DepositionRate,
)

from movpe_IKZ import (
    ExperimentMovpe2IKZ,
    GrowthStepMovpe2IKZ,
    GrowthMovpe2IKZ,
    GrowthMovpe2IKZReference,
    ThinFilmStackMovpe,
    ThinFilmStackMovpeReference,
    ParentSampleReference,
    SubstrateReference,
    SubstrateTemperatureMovpe,
    SampleParametersMovpe,
    BubblerMovpeIKZ,
    GasSourceMovpeIKZ,
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
                BubblerMovpeIKZ(
                    name=growth_run_file.get(
                        f"Bubbler Material{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                    material=CompositeSystemReference(
                        name=growth_run_file.get(
                            f"Bubbler Material{'' if i == 0 else '.' + str(i)}", ""
                        )[line_number],
                    ),
                    vapor_source=CVDBubbler(
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
                    vapor_rate=CVDVaporRate(
                        mass_flow_controller=growth_run_file.get(
                            f"Bubbler MFC{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        rate=[
                            growth_run_file.get(
                                f"Bubbler Molar Flux{'' if i == 0 else '.' + str(i)}", 0
                            )[line_number]
                        ],
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
                GasSourceMovpeIKZ(
                    name=growth_run_file.get(
                        f"Gas Material{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                    material=CompositeSystemReference(
                        name=growth_run_file.get(
                            f"Gas Material{'' if i == 0 else '.' + str(i)}", ""
                        )[line_number],
                    ),
                    vapor_rate=CVDVaporRate(
                        mass_flow_controller=growth_run_file.get(
                            f"Gas MFC{'' if i == 0 else '.' + str(i)}", 0
                        )[line_number],
                        rate=[
                            growth_run_file.get(
                                f"Gas Molar Flux{'' if i == 0 else '.' + str(i)}", 0
                            )[line_number],
                        ],
                    ),
                )
            )
            i += 1
        else:
            break
    return gas_sources
