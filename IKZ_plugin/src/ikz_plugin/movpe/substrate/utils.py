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
from nomad.datamodel.metainfo.basesections import (
    ElementalComposition,
)
from nomad_material_processing.general import (
    Dopant,
)


def populate_element(line_number, substrates_file: pd.DataFrame):
    """
    Populate the GasSource object from the growth run file
    """
    elements = []
    elements_quantities = [
        'Elements',
    ]
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in substrates_file.columns
            for key in elements_quantities
        ):
            element = substrates_file.get(
                f"Elements{'' if i == 0 else '.' + str(i)}", ''
            )[line_number]
            if not pd.isna(element):
                elements.append(
                    ElementalComposition(
                        element=element,
                    )
                )
            i += 1
        else:
            break
    return elements


def populate_dopant(line_number, substrates_file: pd.DataFrame):
    """
    Populate the GasSource object from the growth run file
    """
    dopants = []
    dopant_quantities = [
        'Doping species',
        'Doping Level',
    ]
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in substrates_file.columns
            for key in dopant_quantities
        ):
            doping_species = substrates_file.get(
                f"Doping species{'' if i == 0 else '.' + str(i)}", ''
            )[line_number]
            doping_level = substrates_file.get(
                f"Doping Level{'' if i == 0 else '.' + str(i)}", ''
            )[line_number]
            if not pd.isna(doping_species):
                dopants.append(
                    Dopant(
                        element=doping_species,
                        doping_level=doping_level,
                    )
                )
            i += 1
        else:
            break
    return dopants
