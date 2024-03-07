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

from typing import (
    Dict,
    Any,
    TYPE_CHECKING
)
import numpy as np
from nomad.units import ureg
from pynxtools.dataconverter.convert import transfer_data_into_template

if TYPE_CHECKING:
    from structlog.stdlib import (
        BoundLogger,
    )
#def transfer_data_into_template(**kwargs):
#    raise NotImplementedError

def read_nexus_asc(file_path: str, logger: 'BoundLogger'=None) -> Dict[str, Any]:
    '''
    Function for reading the UV-Vis-NIR transmission data from Perkin-ELmer *.asc in a Nexus file.

    Args:
        file_path (str): The path to the transmission data file.
        logger (BoundLogger, optional): A structlog logger. Defaults to None.

    Returns:
        Dict[str, Any]: The transmission data in a Python dictionary.
    '''
    #nxdl_name = 'NXxrd_pan'
    transmission_template = transfer_data_into_template(
        nxdl_name='NXtransmission',
        input_file=file_path,
        reader='transmission',
    )
    return transmission_template
