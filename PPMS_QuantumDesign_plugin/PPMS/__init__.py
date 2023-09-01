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
from datetime import datetime

from nomad.metainfo import Package, Quantity, MEnum, SubSection, Section, MSection
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.basesections import Activity, CompositeSystem, Measurement, PureSubstance

m_package = Package(name='PPMS')


class Sample(CompositeSystem):
    name = Quantity(
        type=str,
        description='FILL')
    type = Quantity(
        type=str,
        description='FILL')
    material = Quantity(
        type=str,
        description='FILL')
    voltage_lead_preparation = Quantity(
        type=str,
        description='FILL')
    cross_sectional_area = Quantity(
        type=str,
        description='FILL')

class PPMSChannelData(ArchiveSection):
    '''Data section from Channels in PPMS'''
    m_def = Section(
        label_quantity='name',
    )
    name = Quantity(
        type=str,
        description='FILL',
        a_eln={
            "component": "StringEditQuantity"})
    resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description='FILL')
    resistance_std_dev = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description='FILL')
    phase_angle = Quantity(
        type=np.dtype(np.float64),
        unit='deg',
        shape=['*'],
        description='FILL')


class PPMSData(ArchiveSection):
    '''Data section from PPMS'''
    m_def = Section(
        a_eln=dict(lane_width='600px'),
    )
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
    field = Quantity(
        type=np.dtype(np.float64),
        unit='gauss',
        shape=['*'],
        description='FILL')
    sample_position = Quantity(
        type=np.dtype(np.float64),
        unit='deg',
        shape=['*'],
        description='FILL')
    chamber_pressure = Quantity(
        type=np.dtype(np.float64),
        unit='torr',
        shape=['*'],
        description='FILL')
    channels = SubSection(section_def=PPMSChannelData, repeats=True)


class PPMSMeasurement(Measurement, EntryData):
    """A parser for PPMS measurement data"""

    m_def = Section(
        a_eln=dict(lane_width='600px'),
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    file_open_time = Quantity(
        type=str,
        description='FILL')
    software = Quantity(
        type=str,
        description='FILL')
    startupaxis = Quantity(
        type=str,
        shape=['*'],
        description='FILL')


    data = SubSection(section_def=PPMSData)

    def normalize(self, archive, logger):
        super(PPMSMeasurement, self).normalize(archive, logger)

        # def parse_ppms_header(self):

        if archive.data.data_file:
            logger.info('Parsing PPMS measurement file.')
            with archive.m_context.raw_file(self.data_file) as file:
                data = file.read()

            header_match = re.search(r'\[Header\](.*?)\[Data\]', data, re.DOTALL)
            header_section = header_match.group(1).strip()
            header_lines = header_section.split('\n')

            sample1_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE1_' in line]
            if sample1_headers:
                sample_1 = Sample()
                for line in sample1_headers:
                    parts = re.split(r',\s*', line)
                    key = parts[2].lower().replace('SAMPLE1_','')
                    if hasattr(sample_1, key):
                        setattr(sample_1, key, parts[1])

            sample2_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE2_' in line]
            if sample2_headers:
                sample_2 = Sample()
                for line in sample2_headers:
                    parts = re.split(r',\s*', line)
                    key = parts[2].lower().replace('SAMPLE2_','')
                    if hasattr(sample_2, key):
                        setattr(sample_2, key, parts[1])

                while self.samples:
                    self.m_remove_sub_section(PPMSMeasurement.samples, 0)
                self.m_add_sub_section(PPMSMeasurement.samples, sample_1)
                self.m_add_sub_section(PPMSMeasurement.samples, sample_2)

            startupaxis_headers = [line for line in header_lines if line.startswith("STARTUPAXIS")]
            if startupaxis_headers:
                startupaxis = []
                for line in startupaxis_headers:
                    parts = line.split(',', 1)
                    startupaxis.append(parts[1])
                if hasattr(self, 'startupaxis'):
                    setattr(self, 'startupaxis', startupaxis)

            for line in header_lines:
                if line.startswith("FILEOPENTIME"):
                    if hasattr(self, 'datetime'):
                        iso_date = datetime.strptime(line.split(',')[3], "%d/%m/%Y %H:%M:%S")
                        setattr(self, 'datetime', iso_date)
                if line.startswith("BYAPP"):
                    if hasattr(self, 'software'):
                        setattr(self, 'software', line.replace('BYAPP,', ''))

            data_section = header_match.string[header_match.end():]
            data_buffer = StringIO(data_section)
            data_df = pd.read_csv(data_buffer, header=None, skipinitialspace=True)
            # Rename columns using the first row of data
            data_df.columns = data_df.iloc[0]
            data_df = data_df.iloc[1:].reset_index(drop=True)


            print(data_df.keys())

            other_data = [key for key in data_df.keys() if 'Ch1' not in key and 'Ch2' not in key]
            self.data = PPMSData()
            for key in other_data:
                clean_key = key.split('(')[0].strip().lower().replace('time stamp','timestamp')
                if hasattr(self.data, clean_key):
                    setattr(self.data,
                            clean_key,
                            data_df[key] # * ureg(data_template[f'{key}/@units'])
                            )
            channel_1_data = [key for key in data_df.keys() if 'Ch1' in key]
            if channel_1_data:
                channel_1 = PPMSChannelData()
                setattr(channel_1, 'name', 'Channel 1')
                for key in channel_1_data:
                    clean_key = key.split('(')[0].replace('Ch1','').strip().lower().replace(' ','_').replace('3rd','third').replace('2nd','second')
                    if hasattr(channel_1, clean_key):
                        setattr(channel_1,
                                clean_key,
                                data_df[key] # * ureg(data_template[f'{key}/@units'])
                                )
                self.data.m_add_sub_section(PPMSData.channels, channel_1)
            channel_2_data = [key for key in data_df.keys() if 'Ch2' in key]
            if channel_2_data:
                channel_2 = PPMSChannelData()
                setattr(channel_2, 'name', 'Channel 2')
                for key in channel_2_data:
                    clean_key = key.split('(')[0].replace('Ch2','').strip().lower().replace(' ','_').replace('3rd','third').replace('2nd','second')
                    if hasattr(channel_2, clean_key):
                        setattr(channel_2,
                                clean_key,
                                data_df[key] # * ureg(data_template[f'{key}/@units'])
                                )
                self.data.m_add_sub_section(PPMSData.channels, channel_2)

m_package.__init_metainfo__()
