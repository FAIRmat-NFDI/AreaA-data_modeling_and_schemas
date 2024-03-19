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


# The min & max wavelength the instrument can measure
MIN_WAVELENGTH = 190.0
MAX_WAVELENGTH = 3350.0


def read_start_date(metadata: list) -> str:
    """Reads the start date from the metadata"""
    century = str(datetime.now().year // 100)
    formated_date = metadata[3].replace("/", "-")
    return f"{century}{formated_date}T{metadata[4]}000Z"


def read_sample_attenuator(metadata: list) -> int:
    """Reads the sample attenuator from the metadata"""
    return int(metadata[47].split()[0].split(":")[1])


def read_ref_attenuator(metadata: list) -> int:
    """Reads the sample attenuator from the metadata"""
    return int(metadata[47].split()[1].split(":")[1])


def is_depolarizer_on(metadata: list) -> bool:
    """Reads whether the depolarizer was active during the measurement"""
    return metadata[46] == "on"


def read_uv_monochromator_range(metadata: list) -> list:
    """Reads the uv monochromator range from the metadata"""
    monochromator_change = float(metadata[41])
    return [MIN_WAVELENGTH, monochromator_change]


def read_visir_monochromator_range(metadata: list) -> list:
    """Reads the visir monochromator range from the metadata"""
    monochromator_change = float(metadata[41])
    return [monochromator_change, MAX_WAVELENGTH]


def get_d2_range(metadata: list) -> list:
    """Reads the D2 lamp range from the metadata"""
    lamp_change = float(metadata[42])
    return [MIN_WAVELENGTH, lamp_change]


def get_halogen_range(metadata: list) -> list:
    """Reads the halogen lamp range from the metadata"""
    lamp_change = float(metadata[42])
    return [lamp_change, MAX_WAVELENGTH]


METADATA_MAP: Dict[str, Any] = {
    "samplename": 8,
    "/ENTRY[entry]/start_time": read_start_date,
    "/ENTRY[entry]/instrument/sample_attenuator/attenuator_transmission": read_sample_attenuator,
    "/ENTRY[entry]/instrument/ref_attenuator/attenuator_transmission": read_ref_attenuator,
    "/ENTRY[entry]/instrument/common_beam_mask/y_gap": 45,
    "/ENTRY[entry]/instrument/polarizer": 48,
    "/ENTRY[entry]/instrument/common_beam_depolarizer": is_depolarizer_on,
    "/ENTRY[entry]/instrument/spectrometer/GRATING[grating]/wavelength_range": read_uv_monochromator_range,
    "/ENTRY[entry]/instrument/spectrometer/GRATING[grating1]/wavelength_range": read_visir_monochromator_range,
    "/ENTRY[entry]/instrument/SOURCE[source]/type": "D2",
    "/ENTRY[entry]/instrument/SOURCE[source]/wavelength_range": get_d2_range,
    "/ENTRY[entry]/instrument/SOURCE[source1]/type": "halogen",
    "/ENTRY[entry]/instrument/SOURCE[source1]/wavelength_range": get_halogen_range,
}


def data_to_template(data: pd.DataFrame) -> Dict[str, Any]:
    """Builds the data entry dict from the data in a pandas dataframe

    Args:
        data (pd.DataFrame): The dataframe containing the data.

    Returns:
        Dict[str, Any]: The dict with the data paths inside NeXus.
    """
    template: Dict[str, Any] = {}
    template["/ENTRY[entry]/data/@axes"] = "wavelength"
    template["/ENTRY[entry]/data/type"] = "transmission"
    template["/ENTRY[entry]/data/@signal"] = "transmission"
    template["/ENTRY[entry]/data/wavelength"] = data.index.values
    template["/ENTRY[entry]/instrument/spectrometer/wavelength"] = data.index.values
    template["/ENTRY[entry]/data/wavelength/@units"] = "nm"
    template["/ENTRY[entry]/data/transmission"] = data.values[:, 0]
    template["/ENTRY[entry]/instrument/measured_data"] = data.values

    return template


def parse_detector_line(line: str, convert: Callable[[str], Any] = None) -> List[Any]:
    """Parses a detector line from the asc file.

    Args:
        line (str): The line to parse.

    Returns:
        List[Any]: The list of detector settings.
    """
    if convert is None:

        def convert(val):
            return val

    return [convert(s.split("/")[-1]) for s in line.split()]


# pylint: disable=too-many-arguments
def convert_detector_to_template(
    det_type: str,
    slit: str,
    time: float,
    gain: float,
    det_idx: int,
    wavelength_range: List[float],
) -> Dict[str, Any]:
    """Writes the detector settings to the template.

    Args:
        det_type (str): The detector type.
        slit (float): The slit width.
        time (float): The exposure time.
        gain (str): The gain setting.

    Returns:
        Dict[str, Any]: The dictionary containing the data readout from the asc file.
    """
    if det_idx == 0:
        path = "/ENTRY[entry]/instrument/DETECTOR[detector]"
    else:
        path = f"/ENTRY[entry]/instrument/DETECTOR[detector{det_idx}]"
    template: Dict[str, Any] = {}
    template[f"{path}/type"] = det_type
    template[f"{path}/response_time"] = time
    if gain is not None:
        template[f"{path}/gain"] = gain

    if slit == "servo":
        template[f"{path}/slit/type"] = "servo"
    else:
        template[f"{path}/slit/type"] = "fixed"
        template[f"{path}/slit/x_gap"] = float(slit)
        template[f"{path}/slit/x_gap/@units"] = "nm"

    template[f"{path}/wavelength_range"] = wavelength_range

    return template


def read_detectors(metadata: list) -> Dict[str, Any]:
    """Reads detector values from the metadata and writes them into a template
    with the appropriate NeXus path."""

    template: Dict[str, Any] = {}
    detector_slits = parse_detector_line(metadata[31])
    detector_times = parse_detector_line(metadata[32], float)
    detector_gains = parse_detector_line(metadata[35], float)
    detector_changes = [float(x) for x in metadata[43].split()]
    wavelength_ranges = [MIN_WAVELENGTH] + detector_changes[::-1] + [MAX_WAVELENGTH]

    template.update(
        convert_detector_to_template(
            "PMT",
            detector_slits[-1],
            detector_times[-1],
            None,
            2,
            [wavelength_ranges[0], wavelength_ranges[1]],
        )
    )

    for name, idx, slit, time, gain in zip(
        ["PbS", "InGaAs"],
        [1, 0],
        detector_slits[1:],
        detector_times[1:],
        detector_gains[1:],
    ):
        template.update(
            convert_detector_to_template(
                name,
                slit,
                time,
                gain,
                idx,
                [wavelength_ranges[2 - idx], wavelength_ranges[3 - idx]],
            )
        )

    return template


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
            output[path] = metadata[val]
        elif isinstance(val, str):
            output[path] = val
        elif isfunction(val):
            output[path] = val(metadata)
        else:
            print(
                f"WARNING: "
                f"Invalid type value {type(val)} of entry '{path}:{val}' in METADATA_MAP"
            )

    output.update(read_detectors(metadata))
    output.update(data_to_template(data))

    return output
