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

# from .schema import *

import re
from io import StringIO
import numpy as np
import pandas as pd

from nomad.metainfo import Package, Quantity, MEnum, SubSection, Section, MSection
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.eln import Activity, Ensemble, Substance, Measurement

m_package = Package(name='PPMS')


class PPMSHeader(ArchiveSection):
    '''Header section from PPMS'''
    file_open_time = Quantity(
        type=str,
        description='FILL')
    software = Quantity(
        type=str,
        description='FILL')
    sample_1_name = Quantity(
        type=str,
        description='FILL')
    sample_1_type = Quantity(
        type=str,
        description='FILL')
    sample_1_material = Quantity(
        type=str,
        description='FILL')
    sample_1_voltage_lead_preparation = Quantity(
        type=str,
        description='FILL')
    sample_1_cross_sectional_area = Quantity(
        type=str,
        description='FILL')
    sample_2_name = Quantity(
        type=str,
        description='FILL')
    sample_2_type = Quantity(
        type=str,
        description='FILL')
    sample_2_material = Quantity(
        type=str,
        description='FILL')


class PPMSData(ArchiveSection):
    '''Data section from PPMS'''
    timestamp = Quantity(
        type=np.dtype(np.float64),
        unit='second',
        shape=['*'],
        description='FILL')
    temperature = Quantity(
        type=np.dtype(np.float64),
        unit='kelvin',
        shape=['*'],
        description='FILL')


class PPMSMeasurement(Measurement, EntryData, ArchiveSection):
    """A parser for PPMS measurement data"""

    m_def = Section(
        a_eln=dict(lane_width='600px'),
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    header = SubSection(section_def=PPMSHeader)
    data = SubSection(section_def=PPMSData)

    def normalize(self, archive, logger):
        super(PPMSMeasurement, self).normalize(archive, logger)

        if archive.data.data_file:
            logger.info('Parsing PPMS measurement file.')
            with archive.m_context.raw_file(self.data_file) as file:
                data = file.read()

            header_match = re.search(r'\[Header\](.*?)\[Data\]', data, re.DOTALL)
            header_section = header_match.group(1).strip()
            header_lines = header_section.split('\n')
            header_dict = {}
            for line in header_lines:
                if line.strip() != "":
                    key, *values = line.split(',')
                    header_dict[key] = [value.strip() for value in values]

            data_section = header_match.string[header_match.end():]
            data_buffer = StringIO(data_section)
            data_df = pd.read_csv(data_buffer, header=None, skipinitialspace=True)
            # Rename columns using the first row of data
            data_df.columns = data_df.iloc[0]
            data_df = data_df.iloc[1:].reset_index(drop=True)

            # Now you can access the header values using the header_dict
            file_open_time = header_dict['FILEOPENTIME'][1]
            # ... (other header values)

            # Print the data DataFrame and header values
            print("Header Values:")
            print("FILEOPENTIME:", file_open_time)
            # ... (print other header values)

            print("\nData DataFrame:")
            print(data_df)

m_package.__init_metainfo__()
