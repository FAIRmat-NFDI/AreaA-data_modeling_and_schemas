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

import re
from io import StringIO
import numpy as np
import pandas as pd
from datetime import datetime

from structlog.stdlib import (
    BoundLogger,
)
from PPMS.schema import PPMSMeasurement, PPMSData, Sample, ChannelData, clean_channel_keys, ETOData

from nomad.metainfo import Package, Section, MEnum, SubSection

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.data import (
    ArchiveSection,
)

from nomad.metainfo import (
    Package,
    Quantity,
)


from nomad.datamodel.metainfo.basesections import ActivityStep

m_package = Package(name='cpfs_ppms')

class CPFSPPMSMeasurementStep(ActivityStep):
    '''
    A step in the PPMS measurement.
    '''
    pass

class CPFSPPMSMeasurementSetTemperatureStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    temperature_set = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='kelvin'
        ),
    )
    temperature_rate = Quantity(
        type=float,
        unit='kelvin/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='kelvin/minute'
        ),
    )
    mode =  Quantity(
        type=MEnum(
            'Fast Settle',
            'No Overshoot'
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

class CPFSPPMSMeasurementSetMagneticFieldStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    field_set = Quantity(
        type=float,
        unit='tesla',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='tesla'
        ),
    )
    field_rate = Quantity(
        type=float,
        unit='tesla/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='tesla/second'
        ),
    )
    approach =  Quantity(
        type=MEnum(
            'Linear',
            'No Overshoot',
            'Oscillate'
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    end_mode =  Quantity(
        type=MEnum(
            'Persistent',
            'Driven'
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

class CPFSPPMSMeasurementWaitStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    delay = Quantity(
        type=float,
        unit='second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='second'
        ),
    )
    condition_temperature = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
    )
    condition_field = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
    )
    condition_position = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
    )
    condition_chamber = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
    )
    on_error_execute =  Quantity(
        type=MEnum(
            'No Action',
            'Abort',
            'Shutdown',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

class CPFSPPMSMeasurementScanFieldStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    initial_field = Quantity(
        type=float,
        unit='tesla',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='tesla'
        ),
    )
    final_field = Quantity(
        type=float,
        unit='tesla',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='tesla'
        ),
    )
    spacing_code = Quantity(
        type=MEnum(
            'Uniform',
            'H*H',
            'H^1/2',
            '1/H',
            'log(H)',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    #increments = Quantity(
    #    type=float,
    #    unit='tesla',
    #    a_eln=ELNAnnotation(
    #        component='NumberEditQuantity',
    #        defaultDisplayUnit='tesla'
    #    ),
    #)
    number_of_steps =  Quantity(
        type=int,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity'
        ),
    )
    rate = Quantity(
        type=float,
        unit='tesla/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='tesla/second'
        ),
    )
    approach = Quantity(
        type=MEnum(
            'Linear',
            'No Overshoot',
            'Oscillate',
            'Sweep',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    end_mode = Quantity(
        type=MEnum(
            'Persistent',
            'Driven',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

class CPFSPPMSMeasurementScanFieldEndStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    pass

class CPFSPPMSMeasurementScanTempStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    initial_temp = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='kelvin'
        ),
    )
    final_temp = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='kelvin'
        ),
    )
    spacing_code = Quantity(
        type=MEnum(
            'Uniform',
            '1/T',
            'log(T)',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    number_of_steps =  Quantity(
        type=int,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity'
        ),
    )
    rate = Quantity(
        type=float,
        unit='kelvin/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='kelvin/minute'
        ),
    )
    approach = Quantity(
        type=MEnum(
            'Fast',
            'No Overshoot',
            'Sweep',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

class CPFSPPMSMeasurementScanTempEndStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    pass

class CPFSPPMSMeasurementACTResistanceStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    measurement_active = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        shape=[2],
    )
    excitation = Quantity(
        type=float,
        unit='ampere',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='milliampere'
        ),
        shape=[2],
    )
    frequency = Quantity(
        type=float,
        unit='hertz',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='hertz'
        ),
        shape=[2],
    )
    duration = Quantity(
        type=float,
        unit='second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='second'
        ),
        shape=[2],
    )
    constant_current_mode = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        shape=[2],
    )
    low_resistance_mode = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        shape=[2],
    )
    autorange = Quantity(
        type=MEnum(
            'Always Autorange',
            'Sticky Autorange',
            'Fixed Gain',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
        shape=[2],
    )
    fixed_gain = Quantity(
        type=float,
        unit='volt',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='volt'
        ),
        shape=[2],
    )

class CPFSPPMSMeasurementETOResistanceStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    mode = Quantity(
        type=MEnum(
            'Do Nothing',
            'Start Excitation',
            'Start Continuous Measure',
            'Perform N Measurements',
            'Stop Measurement',
            'Stop Excitation',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
        shape=[2],
    )
    excitation_amplitude = Quantity(
        #no unit, either milliAmpere for 4-wire or Volt for 2-wire
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
        shape=[2],
    )
    excitation_frequency = Quantity(
        type=float,
        unit='hertz',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='hertz'
        ),
        shape=[2],
    )
    preamp_range = Quantity(
        #TODO: figure out to read this from sequence file (is in bins 9-11 somehow)
        #no unit, either Volt for 4-wire or Ampere for 2-wire
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity'
        ),
        shape=[2],
    )
    preamp_sample_wiring = Quantity(
        type=MEnum(
            '4-wire',
            '2-wire',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
        shape=[2],
    )
    preamp_autorange = Quantity(
        type=bool,
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        shape=[2],
    )
    config_averaging_time= Quantity(
        type=float,
        unit='second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='second'
        ),
        shape=[2],
    )
    config_number_of_measurements= Quantity(
        type=int,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity'
        ),
        shape=[2],
    )

class CPFSPPMSMeasurementSetPositionStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    position_set = Quantity(
        type=float,
        unit='degree',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='degree'
        ),
    )
    position_rate = Quantity(
        type=float,
        unit='degree/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='degree/minute'
        ),
    )
    mode =  Quantity(
        type=MEnum(
            'Move to position',
            'Move to index and define',
            'Redefine present position'
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )

class CPFSPPMSMeasurementRemarkStep(CPFSPPMSMeasurementStep):
    '''
    A step in the PPMS measurement.
    '''
    remark_text = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )

class CPFSPPMSMeasurement(PPMSMeasurement,EntryData):

    # m_def = Section(
    #     a_eln=dict(lane_width='600px'),
    #     a_plot={"plotly_graph_object": {
    #             "data": {
    #             "x": "#data/temperature",
    #             "y": "#data/field",
    #             },
    #         }
    # },
    # )
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                   'name',
                   'datetime',
                   'end_time',
                   'software',
                   'startupaxis',
               ],
            ),
            lane_width='600px',
            ),
            a_plot=[
                {
                 'layout': { 'title': { 'text': 'Resistance vs. Temperature Channel 1'}},
                'x': 'data/temperature',
                'y': 'data/channels/0/resistance',
                'config': {'editable': True, 'scrollZoom': True,}
                },
                {
                 'layout': { 'title': { 'text': 'Resistance vs. Temperature Channel 2'}},
                'x': 'data/temperature',
                'y': 'data/channels/1/resistance',
                'config': {'editable': True, 'scrollZoom': True,}
                },
                ]
    )

    steps = SubSection(
        section_def=CPFSPPMSMeasurementStep,
        repeats=True,
    )

    data = SubSection(section_def=PPMSData, repeats=True)

    sequence_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    def normalize(self, archive, logger: BoundLogger) -> None:
        #super(CPFSPPMSMeasurement, self).normalize(archive, logger)

        if archive.data.sequence_file:
            logger.info('Parsing PPMS sequence file.')
            with archive.m_context.raw_file(self.sequence_file, 'r') as file:
                sequence = file.readlines()

            all_steps=[]
            measurement_active=False
            for line in sequence:
                if line.startswith("!"):
                    continue
                elif line.startswith("REM "):
                    all_steps.append(CPFSPPMSMeasurementRemarkStep(
                        name="Remark: "+line[4:],
                        remark_text=line[4:],
                        )
                    )
                elif line.startswith("WAI "):
                    details=line.split()
                    onerror=["No Action","Abort","Shutdown"]
                    all_steps.append(CPFSPPMSMeasurementWaitStep(
                        name="Wait for "+details[2]+" s.",
                        delay=float(details[2]),
                        condition_temperature=bool(int(details[3])),
                        condition_field=bool(int(details[4])),
                        condition_position=bool(int(details[5])),
                        condition_chamber=bool(int(details[6])),
                        on_error_execute=onerror[int(details[7])],
                        )
                    )
                elif line.startswith("MVP"):
                    details=line.split()
                    mode=["Move to position","Move to index and define",
                          "Redefine present position"]
                    all_steps.append(CPFSPPMSMeasurementSetPositionStep(
                        name="Move sample to position "+details[2]+".",
                        position_set=float(details[2]),
                        position_rate=float(details[5].strip("\"")),
                        mode=mode[int(details[3])],
                        )
                    )
                elif line.startswith("TMP"):
                    details=line.split()
                    mode=['Fast Settle','No Overshoot']
                    all_steps.append(CPFSPPMSMeasurementSetTemperatureStep(
                        name="Set temperature to "+details[2]+" K with "+details[3]+" K/min.",
                        temperature_set=float(details[2]),
                        temperature_rate=float(details[3])/60.,
                        mode=mode[int(details[4])],
                        )
                    )
                elif line.startswith("FLD"):
                    details=line.split()
                    approach=['Linear','No Overshoot','Oscillate']
                    end_mode=['Persistent','Driven']
                    all_steps.append(CPFSPPMSMeasurementSetMagneticFieldStep(
                        name="Set field to "+details[2]+" Oe with "+details[3]+" Oe/min.",
                        field_set=float(details[2])/10000,
                        field_rate=float(details[3])/10000,
                        approach=approach[int(details[4])],
                        end_mode=end_mode[int(details[5])],
                        )
                    )
                elif line.startswith("LPB"):
                    details=line.split()
                    spacing_code=['Uniform','H*H','H^1/2','1/H','log(H)']
                    approach=['Linear','No Overshoot','Oscillate','Sweep']
                    end_mode=['Persistent','Driven']
                    all_steps.append(CPFSPPMSMeasurementScanFieldStep(
                        name="Scan field from "+details[2]+" Oe to "+details[3]+" Oe.",
                        initial_field=float(details[2])/10000,
                        final_field=float(details[3])/10000,
                        spacing_code=spacing_code[int(details[6])],
                        rate=float(details[4])/10000,
                        number_of_steps=int(details[5]),
                        approach=approach[int(details[7])],
                        end_mode=end_mode[int(details[8])],
                        )
                    )
                elif line.startswith("ENB"):
                    all_steps.append(CPFSPPMSMeasurementScanFieldEndStep(
                        name="End Field Scan."
                        )
                    )
                elif line.startswith("LPT"):
                    details=line.split()
                    spacing_code=['Uniform','1/T','log(T)']
                    approach=['Fast','No Overshoot','Sweep']
                    all_steps.append(CPFSPPMSMeasurementScanTempStep(
                        name="Scan temperature from "+details[2]+" K to "+details[3]+" K.",
                        initial_field=float(details[2]),
                        final_field=float(details[3]),
                        spacing_code=spacing_code[int(details[6])],
                        rate=float(details[4])/60.,
                        number_of_steps=int(details[5]),
                        approach=approach[int(details[7])],
                        )
                    )
                elif line.startswith("ENT"):
                    all_steps.append(CPFSPPMSMeasurementScanTempEndStep(
                        name="End Temperature Scan."
                        )
                    )
                elif line.startswith("ACTR"):
                    details=line.split()
                    autorange=['Fixed Gain','Always Autorange','Sticky Autorange']
                    fixedgain=[5,1,0.5,0.2,0.1,0.05,0.04,0.02,0.01,0.005,0.004,0.002,0.001,0.0004,0.0002,0.00004]
                    all_steps.append(CPFSPPMSMeasurementACTResistanceStep(
                        name="AC Transport Resistance measurement.",
                        measurement_active=[bool(int(details[4])),bool(int(details[12]))],
                        excitation=[float(details[5])/1000,float(details[13])/1000],
                        frequency=[float(details[6]),float(details[14])],
                        duration=[float(details[7]),float(details[15])],
                        constant_current_mode=[bool(int(details[8])),bool(int(details[16]))],
                        low_resistance_mode=[bool(int(details[11])),bool(int(details[19]))],
                        autorange=[autorange[int(details[9])],autorange[int(details[17])]],
                        fixed_gain=[fixedgain[int(details[10])],fixedgain[int(details[18])]]
                        )
                    )
                elif line.startswith("ETOR"):
                    details=line.split()
                    mode=['Do Nothing','Start Excitation','Start Continuous Measure',
                          'Perform N Measurements','Stop Measurement','Stop Excitation']
                    sample_wiring=['4-wire','2-wire']
                    shift=0
                    name=""
                    mode_int=[]
                    number_of_measure=[]
                    amplitude=[]
                    frequency=[]
                    wiring=[]
                    autorange=[]
                    averaging_time=[]
                    for i in range(2):
                        mode_int.append(int(details[3+shift]))
                        if mode_int[i] in [0,4,5]:
                            number_of_measure.append(0)
                            amplitude.append(0)
                            frequency.append(0)
                            wiring.append(0)
                            autorange.append(False)
                            averaging_time.append(0)
                            shift+=1
                        elif mode_int[i] in [1,2,3]:
                            if mode_int[i]==3:
                                number_of_measure.append(int(details[4+shift]))
                                shift+=1
                            else:
                                number_of_measure.append(0)
                            amplitude.append(float(details[5+shift])/1000.)
                            frequency.append(float(details[6+shift]))
                            wiring.append(int(details[12+shift]))
                            autorange.append(bool(int(details[8+shift])))
                            averaging_time.append(float(details[7+shift]))
                            shift+=10
                        name+="Channel "+str(i+1)+": "+mode[mode_int[i]]
                        if i==0: name+="; "
                    # if 4 in mode_int:
                    #     measurement_active=False
                    # if 1 in mode_int or 2 in mode_int or 3 in mode_int:
                    #     measurement_active=True
                    all_steps.append(CPFSPPMSMeasurementETOResistanceStep(
                        name=name,
                        mode=[mode[mode_int[0]],mode[mode_int[1]]],
                        excitation_amplitude=amplitude,
                        excitation_frequency=frequency,
                        preamp_sample_wiring=[sample_wiring[wiring[0]],sample_wiring[wiring[1]]],
                        preamp_autorange=autorange,
                        config_averaging_time=averaging_time,
                        config_number_of_measurements=number_of_measure,
                        )
                    )
                elif line.startswith("SHT"):
                    continue
                else:
                    logger.error('Found unknown keyword '+line[:4])
            self.steps=all_steps

        if archive.data.data_file:
            logger.info('Parsing PPMS measurement file.')
            with archive.m_context.raw_file(self.data_file, 'r') as file:
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
                        iso_date = datetime.strptime(line.split(',')[3], "%m/%d/%Y %H:%M:%S")
                        setattr(self, 'datetime', iso_date)
                if line.startswith("BYAPP"):
                    if hasattr(self, 'software'):
                        setattr(self, 'software', line.replace('BYAPP,', ''))

            data_section = header_match.string[header_match.end():]
            data_buffer = StringIO(data_section)
            data_df = pd.read_csv(data_buffer, header=None, skipinitialspace=True, sep=',',engine='python')
            # Rename columns using the first row of data
            data_df.columns = data_df.iloc[0]
            data_df = data_df.iloc[1:].reset_index(drop=True)


            print(data_df.keys())

            other_data = [key for key in data_df.keys() if 'Ch1' not in key and 'Ch2' not in key and 'ETO Channel' not in key]
            self.data = PPMSData()
            for key in other_data:
                clean_key = key.split('(')[0].strip().replace(' ','_').lower().replace('time stamp','timestamp')
                if hasattr(self.data, clean_key):
                    setattr(self.data,
                            clean_key,
                            data_df[key] # * ureg(data_template[f'{key}/@units'])
                            )
            channel_1_data = [key for key in data_df.keys() if 'Ch1' in key]
            if channel_1_data:
                channel_1 = ChannelData()
                setattr(channel_1, 'name', 'Channel 1')
                for key in channel_1_data:
                    clean_key = clean_channel_keys(key)
                    if hasattr(channel_1, clean_key):
                        setattr(channel_1,
                                clean_key,
                                data_df[key] # * ureg(data_template[f'{key}/@units'])
                                )
                self.data.m_add_sub_section(PPMSData.channels, channel_1)
            channel_2_data = [key for key in data_df.keys() if 'Ch2' in key]
            if channel_2_data:
                channel_2 = ChannelData()
                setattr(channel_2, 'name', 'Channel 2')
                for key in channel_2_data:
                    clean_key = clean_channel_keys(key)
                    if hasattr(channel_2, clean_key):
                        setattr(channel_2,
                                clean_key,
                                data_df[key] # * ureg(data_template[f'{key}/@units'])
                                )
                self.data.m_add_sub_section(PPMSData.channels, channel_2)
            eto_channel_data = [key for key in data_df.keys() if 'ETO Channel' in key]
            if eto_channel_data:
                for key in eto_channel_data:
                    eto_channel = ETOData()
                    if hasattr(eto_channel, 'name'):
                        setattr(eto_channel, 'name', key)
                    if hasattr(eto_channel, 'ETO_channel'):
                        setattr(eto_channel, 'ETO_channel', data_df[key])
                    self.data.m_add_sub_section(PPMSData.eto_channels, eto_channel)


m_package.__init_metainfo__()