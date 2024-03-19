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

from typing import Dict, Any, TYPE_CHECKING
from datetime import datetime
from inspect import isfunction
from typing import Callable, List, Any, Dict
import numpy as np
from nomad.units import ureg
import pandas as pd

if TYPE_CHECKING:
    from structlog.stdlib import (
        BoundLogger,
    )


def read_sample_name(metadata: list) -> str:
    """Reads the sample name from the metadata"""
    if not metadata[2]:
        return None
    return metadata[2].split(".")[0]


def read_start_datetime(metadata: list) -> str:
    """Reads the start date from the metadata"""
    if not metadata[3] or not metadata[4]:
        return None
    century = str(datetime.now().year // 100)
    formated_date = metadata[3].replace("/", "-")
    return f"{century}{formated_date}T{metadata[4]}000Z"


def read_is_D2_lamp_on(metadata: list) -> bool:
    """Reads whether the D2 lamp was active during the measurement"""
    if not metadata[21]:
        return None
    return bool(float(metadata[21]))


def read_is_tungsten_lamp_on(metadata: list) -> bool:
    """Reads whether the tungsten lamp was active during the measurement"""
    if not metadata[22]:
        return None
    return bool(float(metadata[22]))


def read_sample_attenuation_percentage(metadata: list) -> int:
    """Reads the sample attenuation percentage from the metadata"""
    if not metadata[47]:
        return None
    return int(metadata[47].split()[0].split(":")[1])


def read_reference_attenuation_percentage(metadata: list) -> int:
    """Reads the sample attenuation percentage from the metadata"""
    if not metadata[47]:
        return None
    return int(metadata[47].split()[1].split(":")[1])


def read_is_depolarizer_on(metadata: list) -> bool:
    """Reads whether the depolarizer was active during the measurement"""
    if not metadata[46]:
        return False
    return metadata[46] == "on"


METADATA_MAP: Dict[str, Any] = {
    "sample_name": read_sample_name,
    "start_datetime": read_start_datetime,
    "analyst_name": 7,
    "instrument_name": 11,
    "instrument_serial_number": 12,
    "instrument_firmware_version": 13,
    "is_D2_lamp_on": read_is_D2_lamp_on,
    "is_tungsten_lamp_on": read_is_tungsten_lamp_on,
    "sample_beam_position": 44,
    "common_beam_mask_percentage": 45,
    "is_common_beam_depolarizer_on": read_is_depolarizer_on,
    "sample_attenuation_percentage": read_sample_attenuation_percentage,
    "reference_attenuation_percentage": read_reference_attenuation_percentage,
    "polarizer_angle": 48,
    "ordinate": 80,
    "wavelength_units": 79,
    "monochromator_change_wavelength": 41,
    "lamp_change_wavelength": 42,
}


def data_to_template(data: pd.DataFrame) -> Dict[str, Any]:
    """Builds the data entry dict from the data in a pandas dataframe

    Args:
        data (pd.DataFrame): The dataframe containing the data.

    Returns:
        Dict[str, Any]: The dict with the data paths inside NeXus.
    """
    output: Dict[str, Any] = {}
    output["measured_wavelength"] = data.index.values
    output["measured_ordinate"] = data.values[:, 0]

    return output


def parse_detector_line(line: str) -> Dict[str, float]:
    """Parses a detector line from the asc file. Generates a dict where each key-value
    pair is the detector setting (value) for the corresponding wavelength (key).
    Eg. {"600": 0.5, "1050": 1.0}

    Args:
        line (str): The line to parse.

    Returns:
        Dict[str, float]: The dict of detector settings with wavelength as key.
    """

    def convert(val):
        val_list = val.strip().split("/")
        return {val_list[0]: float(val_list[1])}

    output = dict()
    for s in line.split():
        output.update(convert(s))
    return output


def read_detectors(metadata: list) -> Dict[str, Any]:
    """
    Reads detector values from the metadata


    Args:
        metadata (list): Metadata lines extracted from the asc file.

    Returns:
        Dict[str, Any]: The dictionary containing the detector metadata.
    """

    output: Dict[str, Any] = {}
    if metadata[31]:
        output["detector_slit_width"] = parse_detector_line(metadata[31])
    if metadata[32]:
        output["detector_integration_time"] = parse_detector_line(metadata[32])
    if metadata[35]:
       output["detector_NIR_gain"] = parse_detector_line(metadata[35])
    if metadata[43]:
        output["detector_change_wavelength"] = np.array(
            [float(x) for x in metadata[43].split()]
        )

    return output


def read_asc(file_path: str, logger: "BoundLogger" = None) -> Dict[str, Any]:
    """
    Function for reading the transmission data from PerkinElmer *.asc.

    Args:
        file_path (str): The path to the transmission data file.
        logger (BoundLogger, optional): A structlog logger. Defaults to None.

    Returns:
        Dict[str, Any]: The transmission data and metadata in a Python dictionary.
    """

    output: Dict[str, Any] = {}
    data_start_ind = "#DATA"

    with open(file_path, encoding="utf-8") as file_obj:
        metadata = []
        for line in file_obj:
            if line.strip() == data_start_ind:
                break
            metadata.append(line.strip())

        data = pd.read_csv(file_obj, delim_whitespace=True, header=None, index_col=0)

    for path, val in METADATA_MAP.items():
        # If the dict value is an int just get the data with it's index
        if isinstance(val, int):
            if metadata[val]:
                try:
                    output[path] = float(metadata[val])
                except ValueError:
                    output[path] = metadata[val]
        elif isinstance(val, str):
            output[path] = val
        elif isfunction(val):
            output[path] = val(metadata)
        else:
            raise ValueError(
                f"Invalid type value {type(val)} of entry '{path}:{val}' in METADATA_MAP"
            )

    output.update(read_detectors(metadata))
    output.update(data_to_template(data))

    return output
