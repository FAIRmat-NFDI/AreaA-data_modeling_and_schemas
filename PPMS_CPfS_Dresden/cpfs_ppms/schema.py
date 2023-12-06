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
#from PPMS.schema import PPMSMeasurement, PPMSData, Sample, ChannelData, ETOData

from nomad.metainfo import Package, Section, MEnum, SubSection

from nomad.datamodel.metainfo.basesections import Measurement

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

from nomad.datamodel.metainfo.eln import (
    CompositeSystem,
)

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from nomad.datamodel.metainfo.basesections import ActivityStep

m_package = Package(name='cpfs_ppms')

def clean_channel_keys(input_key: str) -> str:
    output_key = (
        input_key
        .split('(')[0]
        .replace('Std. Dev.', 'std dev')
        .replace('Std.Dev.', 'std dev')
        .replace('Res.', 'resistivity')
        .replace('Crit.Cur.', 'crit cur')
        .replace('C.Cur.', 'crit cur')
        .replace('Quad.Error', 'quad error')
        .replace('Harm.', 'harmonic')
        .replace('-', ' ')
        .lower()
        .replace('ch1','')
        .replace('ch2','')
        .strip()
        .replace(' ','_')
        .replace('3rd','third')
        .replace('2nd','second')
    )
    return output_key

class CPFSSample(CompositeSystem):
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
        unit='gauss',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gauss'
        ),
    )
    field_rate = Quantity(
        type=float,
        unit='gauss/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gauss/second'
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
        unit='gauss',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gauss'
        ),
    )
    final_field = Quantity(
        type=float,
        unit='gauss',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gauss'
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
        unit='gauss/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gauss/second'
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

class CPFSPPMSData(ArchiveSection):
    '''General data section from PPMS'''
    name = Quantity(
        type=str,
        description='FILL',
        a_eln={
            "component": "StringEditQuantity"}
        )

class CPFSETOData(ArchiveSection):
    '''Data section from Channels in PPMS'''
    m_def = Section(
        label_quantity='name',
    )
    name = Quantity(
        type=str,
        description='FILL',
        a_eln={
            "component": "StringEditQuantity"}
        )
    eto_channel = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')

class CPFSETOChannelData(ArchiveSection):
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
    i_v_current = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    i_v_voltage = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description='FILL')
    frequency = Quantity(
        type=np.dtype(np.float64),
        unit='Hz',
        shape=['*'],
        description='FILL')
    averaging_time = Quantity(
        type=np.dtype(np.float64),
        unit='second',
        shape=['*'],
        description='FILL')
    ac_current = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    dc_current = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    current_ampl = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    in_phase_current = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    quadrature_current = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    gain = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    second_harmonic = Quantity(
        type=np.dtype(np.float64),
        unit='dB',
        shape=['*'],
        description='FILL')
    third_harmonic = Quantity(
        type=np.dtype(np.float64),
        unit='dB',
        shape=['*'],
        description='FILL')

class CPFSETOPPMSData(CPFSPPMSData):
    '''Data section from PPMS'''
    m_def = Section(
        a_eln=dict(lane_width='600px'),
    )
    time_stamp = Quantity(
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
    eto_measurement_mode = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    temperature_status = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    field_status = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    chamber_status = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    eto_status_code = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    channels = SubSection(section_def=CPFSETOChannelData, repeats=True)
    eto_channels = SubSection(section_def=CPFSETOData, repeats=True)

class CPFSACTData(ArchiveSection):
    '''Data section from Channels in PPMS'''
    m_def = Section(
        label_quantity='name',
    )
    name = Quantity(
        type=str,
        description='FILL',
        a_eln={
            "component": "StringEditQuantity"})
    map = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')

class CPFSACTChannelData(ArchiveSection):
    '''Data section from Channels in PPMS'''
    m_def = Section(
        label_quantity='name',
    )
    name = Quantity(
        type=str,
        description='FILL',
        a_eln={
            "component": "StringEditQuantity"})
    volts = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description='FILL')
    v_std_dev = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description='FILL')
    resistivity = Quantity(
        type=np.dtype(np.float64),
        unit='ohm/centimeter',
        shape=['*'],
        description='FILL')
    resistivity_std_dev = Quantity(
        type=np.dtype(np.float64),
        unit='ohm/centimeter',
        shape=['*'],
        description='FILL')
    hall = Quantity(
        type=np.dtype(np.float64),
        unit='centimeter**3/coulomb',
        shape=['*'],
        description='FILL')
    hall_std_dev = Quantity(
        type=np.dtype(np.float64),
        unit='centimeter**3/coulomb',
        shape=['*'],
        description='FILL')
    crit_cur = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    crit_cur_std_dev = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    second_harmonic = Quantity(
        type=np.dtype(np.float64),
        unit='dB',
        shape=['*'],
        description='FILL')
    third_harmonic = Quantity(
        type=np.dtype(np.float64),
        unit='dB',
        shape=['*'],
        description='FILL')
    quad_error = Quantity(
        type=np.dtype(np.float64),
        unit='ohm/cm/rad',
        shape=['*'],
        description='FILL')
    drive_signal = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description='FILL')

class CPFSACTPPMSData(CPFSPPMSData):
    '''Data section from PPMS'''
    m_def = Section(
        a_eln=dict(lane_width='600px'),
    )
    measurement_type = Quantity(
        type=MEnum(
            'temperature',
            'field',
            ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    time_stamp = Quantity(
        type=np.dtype(np.float64),
        unit='second',
        shape=['*'],
        description='FILL')
    status = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    temperature = Quantity(
        type=np.dtype(np.float64),
        unit='kelvin',
        shape=['*'],
        description='FILL')
    magnetic_field = Quantity(
        type=np.dtype(np.float64),
        unit='gauss',
        shape=['*'],
        description='FILL')
    sample_position = Quantity(
        type=np.dtype(np.float64),
        unit='deg',
        shape=['*'],
        description='FILL')
    excitation = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    frequency = Quantity(
        type=np.dtype(np.float64),
        unit='Hz',
        shape=['*'],
        description='FILL')
    act_status = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    act_gain = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    bridge_1_resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description='FILL')
    bridge_2_resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description='FILL')
    bridge_3_resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description='FILL')
    bridge_4_resistance = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description='FILL')
    bridge_1_excitation = Quantity(
        type=np.dtype(np.float64),
        unit='microampere',
        shape=['*'],
        description='FILL')
    bridge_2_excitation = Quantity(
        type=np.dtype(np.float64),
        unit='microampere',
        shape=['*'],
        description='FILL')
    bridge_3_excitation = Quantity(
        type=np.dtype(np.float64),
        unit='microampere',
        shape=['*'],
        description='FILL')
    bridge_4_excitation = Quantity(
        type=np.dtype(np.float64),
        unit='microampere',
        shape=['*'],
        description='FILL')
    signal_1_vin = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description='FILL')
    signal_2_vin = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description='FILL')
    digital_inputs = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='FILL')
    drive_1_iout = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    drive_2_iout = Quantity(
        type=np.dtype(np.float64),
        unit='mA',
        shape=['*'],
        description='FILL')
    drive_1_ipower = Quantity(
        type=np.dtype(np.float64),
        unit='watts',
        shape=['*'],
        description='FILL')
    drive_2_ipower = Quantity(
        type=np.dtype(np.float64),
        unit='watts',
        shape=['*'],
        description='FILL')
    pressure = Quantity(
        type=np.dtype(np.float64),
        unit='torr',
        shape=['*'],
        description='FILL')
    channels = SubSection(section_def=CPFSACTChannelData, repeats=True)
    maps = SubSection(section_def=CPFSACTData, repeats=True)



class CPFSPPMSMeasurement(Measurement,PlotSection,EntryData):

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
                   'data_file',
                   'sequence_file',
                   'description',
                   'software',
                   'startupaxis',
               ],
            ),
            lane_width='600px',
            ),
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

    steps = SubSection(
        section_def=CPFSPPMSMeasurementStep,
        repeats=True,
    )

    data = SubSection(section_def=CPFSPPMSData, repeats=True)
    #data = SubSection(section_def=CPFSPPMSData)

    sequence_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    temperature_tolerance = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='kelvin'
        ),
    )

    field_tolerance = Quantity(
        type=float,
        unit='gauss',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gauss'
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:

        super(CPFSPPMSMeasurement, self).normalize(archive, logger)

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
                        field_set=float(details[2]),
                        field_rate=float(details[3]),
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
                        initial_field=float(details[2]),
                        final_field=float(details[3]),
                        spacing_code=spacing_code[int(details[6])],
                        rate=float(details[4]),
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
                        initial_temp=float(details[2]),
                        final_temp=float(details[3]),
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
                elif line.startswith("CHN"):
                    continue
                else:
                    logger.error('Found unknown keyword '+line[:4])
            self.steps=all_steps

        if archive.data.data_file and archive.data.sequence_file:
            logger.info('Parsing PPMS measurement file using the sequence file.')
            if not self.temperature_tolerance:
                self.temperature_tolerance=0.01
            if not self.field_tolerance:
                self.field_tolerance=5.

            with archive.m_context.raw_file(self.data_file, 'r') as file:
                data = file.read()

            header_match = re.search(r'\[Header\](.*?)\[Data\]', data, re.DOTALL)
            header_section = header_match.group(1).strip()
            header_lines = header_section.split('\n')

            sample1_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE1_' in line]
            if sample1_headers:
                sample_1 = CPFSSample()
                for line in sample1_headers:
                    parts = re.split(r',\s*', line)
                    key = parts[2].lower().replace('SAMPLE1_','')
                    if hasattr(sample_1, key):
                        setattr(sample_1, key, parts[1])

            sample2_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE2_' in line]
            if sample2_headers:
                sample_2 = CPFSSample()
                for line in sample2_headers:
                    parts = re.split(r',\s*', line)
                    key = parts[2].lower().replace('SAMPLE2_','')
                    if hasattr(sample_2, key):
                        setattr(sample_2, key, parts[1])

                while self.samples:
                    self.m_remove_sub_section(CPFSPPMSMeasurement.samples, 0)
                self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample_1)
                self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample_2)

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
                        try:
                            iso_date = datetime.strptime(line.split(',')[3], "%m/%d/%Y %H:%M:%S")
                        except ValueError:
                            iso_date = datetime.strptime(" ".join(line.split(',')[2:4]), "%m-%d-%Y %I:%M %p")
                        setattr(self, 'datetime', iso_date)
                if line.startswith("BYAPP"):
                    if hasattr(self, 'software'):
                        setattr(self, 'software', line.replace('BYAPP,', '').strip())

            data_section = header_match.string[header_match.end():]
            data_buffer = StringIO(data_section)
            data_df = pd.read_csv(data_buffer, header=None, skipinitialspace=True, sep=',',engine='python')
            # Rename columns using the first row of data
            data_df.columns = data_df.iloc[0]
            data_df = data_df.iloc[1:].reset_index(drop=True)

            if self.software.startswith("ACTRANSPORT"):
                other_data = [key for key in data_df.keys() if 'ch1' not in key and 'ch2' not in key and 'map' not in key.lower()]
                all_data=[]
                #identify separate measurements by following the steps structure
                temp=float(data_df["Temperature (K)"].iloc[0])*self.temperature_tolerance.units
                field=float(data_df["Magnetic Field (Oe)"].iloc[0])*self.field_tolerance.units
                startval=0
                index=0
                measurement_type="undefined"
                measurement_active=False
                for step in self.steps:
                    measurement_ends=False
                    if isinstance(step,CPFSPPMSMeasurementSetTemperatureStep):
                        if measurement_active:
                            if measurement_type!="undefined" and measurement_type!="temperature":
                                logger.error("Mixed measurement type found. Are sequence and data matching?")
                            measurement_type="temperature"
                            for i in range(index,len(data_df)):
                                if (abs(float(data_df["Temperature (K)"].iloc[i])*step.temperature_set.units-step.temperature_set)<self.temperature_tolerance and
                                    abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*self.field_tolerance.units-field)<self.field_tolerance):
                                    index=i
                                    break
                            else:
                                logger.error("Set temperature not found. Are sequence and data matching?")
                            for i in range(index,len(data_df)):
                                if (abs(float(data_df["Temperature (K)"].iloc[i])*step.temperature_set.units-step.temperature_set)>self.temperature_tolerance or
                                    abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*self.field_tolerance.units-field)>self.field_tolerance):
                                    index=i
                                    break
                            else:
                                index=i
                        temp=step.temperature_set
                    if isinstance(step,CPFSPPMSMeasurementSetMagneticFieldStep):
                        if measurement_active:
                            if measurement_type!="undefined" and measurement_type!="field":
                                logger.error("Mixed measurement type found. Are sequence and data matching?")
                            measurement_type="field"
                            for i in range(index,len(data_df)):
                                if (abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*step.field_set.units-step.field_set)<self.field_tolerance and
                                    abs(float(data_df["Temperature (K)"].iloc[i])*self.temperature_tolerance.units-temp)<self.temperature_tolerance):
                                    index=i
                                    break
                            else:
                                logger.error("Set field not found. Are sequence and data matching?")
                            for i in range(index,len(data_df)):
                                if (abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*step.field_set.units-step.field_set)>self.field_tolerance or
                                    abs(float(data_df["Temperature (K)"].iloc[i])*self.temperature_tolerance.units-temp)>self.temperature_tolerance):
                                    index=i
                                    break
                            else:
                                index=i
                        field=step.field_set
                    if isinstance(step,CPFSPPMSMeasurementScanTempStep):
                        if measurement_active:
                            logger.error("Measurement already active when approaching scan step. Is this sequence valid?")
                        measurement_active=True
                        measurement_type="temperature"
                        if abs(float(data_df["Temperature (K)"].iloc[index])*step.initial_temp.units-step.initial_temp)>self.temperature_tolerance:
                            logger.error("Initial temperature not found in scan step. Are sequence and data matching?")
                        for i in range(index,len(data_df)):
                            if (abs(float(data_df["Temperature (K)"].iloc[i])*step.initial_temp.units-step.final_temp)<self.temperature_tolerance and
                                abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*self.field_tolerance.units-field)<self.field_tolerance):
                                index=i
                                break
                        else:
                            logger.error("Set temperature not found. Are sequence and data matching?")
                        for i in range(index,len(data_df)):
                            if (abs(float(data_df["Temperature (K)"].iloc[i])*step.initial_temp.units-step.final_temp)>self.temperature_tolerance or
                                abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*self.field_tolerance.units-field)>self.field_tolerance):
                                index=i
                                break
                        else:
                            index=i
                        temp=step.final_temp
                    if isinstance(step,CPFSPPMSMeasurementScanFieldStep):
                        if measurement_active:
                            logger.error("Measurement already active when approaching scan step. Is this sequence valid?")
                        measurement_active=True
                        measurement_type="field"
                        if abs(float(data_df["Magnetic Field (Oe)"].iloc[index])*step.initial_field.units-step.initial_field)>self.field_tolerance:
                            logger.error("Initial field not found in scan step. Are sequence and data matching?")
                        for i in range(index,len(data_df)):
                            if (abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*step.initial_field.units-step.final_field)<self.field_tolerance and
                                abs(float(data_df["Temperature (K)"].iloc[i])*self.temperature_tolerance.units-temp)<self.temperature_tolerance):
                                index=i
                                break
                        else:
                            logger.error("Set field not found. Are sequence and data matching?")
                        for i in range(index,len(data_df)):
                            if (abs(float(data_df["Magnetic Field (Oe)"].iloc[i])*step.initial_field.units-step.final_field)>self.field_tolerance or
                                abs(float(data_df["Temperature (K)"].iloc[i])*self.temperature_tolerance.units-temp)>self.temperature_tolerance):
                                index=i
                                break
                        else:
                            index=i
                        field=step.final_field
                    if isinstance(step,CPFSPPMSMeasurementETOResistanceStep):
                        if "Stop Measurement" in step.mode:
                            measurement_ends=False
                        if "Start Continuous Measure" in step.mode or "Perform N Measurements" in step.mode:
                            measurement_active=True
                    if isinstance(step,CPFSPPMSMeasurementScanTempEndStep):
                        if not measurement_active:
                            logger.error("Measurement not running when approaching scan end step. Is this sequence valid?")
                        if measurement_active:
                            if measurement_type!="undefined" and measurement_type!="temperature":
                                logger.error("Mixed measurement type found. Are sequence and data matching?")
                        measurement_ends=True
                    if isinstance(step,CPFSPPMSMeasurementScanFieldEndStep):
                        if not measurement_active:
                            logger.error("Measurement not running when approaching scan end step. Is this sequence valid?")
                        if measurement_active:
                            if measurement_type!="undefined" and measurement_type!="field":
                                logger.error("Mixed measurement type found. Are sequence and data matching?")
                        measurement_ends=True
                    if measurement_ends:
                        measurement_active=False
                        logger.info(startval,index)
                        block=data_df.iloc[startval:index]
                        startval=index
                        data = CPFSACTPPMSData()
                        data.measurement_type=measurement_type
                        if measurement_type=="field":
                            data.name="Field sweep at "+str(temp.magnitude)+" K."
                        if measurement_type=="temperature":
                            data.name="Temperature sweep at "+str(field.magnitude)+" Oe."
                        data.title=data.name
                        for key in other_data:
                            clean_key = key.split('(')[0].strip().replace(' ','_').lower()#.replace('time stamp','timestamp')
                            if hasattr(data, clean_key):
                                setattr(data,
                                        clean_key,
                                        block[key] # * ureg(data_template[f'{key}/@units'])
                                        )
                        channel_1_data = [key for key in block.keys() if 'ch1' in key.lower()]
                        if channel_1_data:
                            channel_1 = CPFSACTChannelData()
                            setattr(channel_1, 'name', 'Channel 1')
                            for key in channel_1_data:
                                clean_key = clean_channel_keys(key)
                                if hasattr(channel_1, clean_key):
                                    setattr(channel_1,
                                            clean_key,
                                            block[key] # * ureg(data_template[f'{key}/@units'])
                                            )
                            data.m_add_sub_section(CPFSACTPPMSData.channels, channel_1)
                        channel_2_data = [key for key in block.keys() if 'ch2' in key.lower()]
                        if channel_2_data:
                            channel_2 = CPFSACTChannelData()
                            setattr(channel_2, 'name', 'Channel 2')
                            for key in channel_2_data:
                                clean_key = clean_channel_keys(key)
                                if hasattr(channel_2, clean_key):
                                    setattr(channel_2,
                                            clean_key,
                                            block[key] # * ureg(data_template[f'{key}/@units'])
                                            )
                            data.m_add_sub_section(CPFSACTPPMSData.channels, channel_2)

                        map_data = [key for key in block.keys() if 'Map' in key]
                        if map_data:
                            for key in map_data:
                                map = CPFSACTData()
                                if hasattr(map, 'name'):
                                    setattr(map, 'name', key)
                                if hasattr(map, 'map'):
                                    setattr(map, 'map', block[key])
                                data.m_add_sub_section(CPFSACTPPMSData.maps, map)

                        all_data.append(data)

                self.data=all_data

                #Now create the according plots
                import plotly.express as px
                from plotly.subplots import make_subplots
                for data in self.data:
                    if data.measurement_type=="field":
                        resistivity_ch1=px.scatter(x=data.magnetic_field,y=data.channels[0].resistivity)
                        resistivity_ch2=px.scatter(x=data.magnetic_field,y=data.channels[1].resistivity)
                    if data.measurement_type=="temperature":
                        resistivity_ch1=px.scatter(x=data.temperature,y=data.channels[0].resistivity)
                        resistivity_ch2=px.scatter(x=data.temperature,y=data.channels[1].resistivity)
                    figure1 = make_subplots(rows=2, cols=1, shared_xaxes=True)
                    figure1.add_trace(resistivity_ch1.data[0], row=1, col=1)
                    figure1.add_trace(resistivity_ch2.data[0], row=2, col=1)
                    figure1.update_layout(height=400, width=716, title_text=data.name)
                    self.figures.append(PlotlyFigure(label=data.name, figure=figure1.to_plotly_json()))



















            # if self.software.startswith("Electrical Transport Option"):
            #     self.data = CPFSETOPPMSData()
            # elif self.software.startswith("ACTRANSPORT"):
            #     self.data = CPFSACTPPMSData()
            # else:
            #     logger.error("Software not recognized: "+self.software)
            # for key in other_data:
            #     clean_key = key.split('(')[0].strip().replace(' ','_').lower()#.replace('time stamp','timestamp')
            #     if hasattr(self.data, clean_key):
            #         setattr(self.data,
            #                 clean_key,
            #                 data_df[key] # * ureg(data_template[f'{key}/@units'])
            #                 )
            # channel_1_data = [key for key in data_df.keys() if 'ch1' in key.lower()]
            # if channel_1_data:
            #     if self.software.startswith("Electrical Transport Option"):
            #         channel_1 = CPFSETOChannelData()
            #     elif self.software.startswith("ACTRANSPORT"):
            #         channel_1 = CPFSACTChannelData()
            #     setattr(channel_1, 'name', 'Channel 1')
            #     for key in channel_1_data:
            #         clean_key = clean_channel_keys(key)
            #         if hasattr(channel_1, clean_key):
            #             setattr(channel_1,
            #                     clean_key,
            #                     data_df[key] # * ureg(data_template[f'{key}/@units'])
            #                     )
            #     if self.software.startswith("Electrical Transport Option"):
            #         self.data.m_add_sub_section(CPFSETOPPMSData.channels, channel_1)
            #     elif self.software.startswith("ACTRANSPORT"):
            #         self.data.m_add_sub_section(CPFSACTPPMSData.channels, channel_1)
            # channel_2_data = [key for key in data_df.keys() if 'ch2' in key.lower()]
            # if channel_2_data:
            #     if self.software.startswith("Electrical Transport Option"):
            #         channel_2 = CPFSETOChannelData()
            #     elif self.software.startswith("ACTRANSPORT"):
            #         channel_2 = CPFSACTChannelData()
            #     setattr(channel_2, 'name', 'Channel 2')
            #     for key in channel_2_data:
            #         clean_key = clean_channel_keys(key)
            #         if hasattr(channel_2, clean_key):
            #             setattr(channel_2,
            #                     clean_key,
            #                     data_df[key] # * ureg(data_template[f'{key}/@units'])
            #                     )
            #     if self.software.startswith("Electrical Transport Option"):
            #         self.data.m_add_sub_section(CPFSETOPPMSData.channels, channel_2)
            #     elif self.software.startswith("ACTRANSPORT"):
            #         self.data.m_add_sub_section(CPFSACTPPMSData.channels, channel_2)


            # if self.software.startswith("Electrical Transport Option"):
            #     eto_channel_data = [key for key in data_df.keys() if 'ETO Channel' in key]
            #     if eto_channel_data:
            #         for key in eto_channel_data:
            #             eto_channel = CPFSETOData()
            #             if hasattr(eto_channel, 'name'):
            #                 setattr(eto_channel, 'name', key)
            #             if hasattr(eto_channel, 'eto_channel'):
            #                 setattr(eto_channel, 'eto_channel', data_df[key])
            #             self.data.m_add_sub_section(CPFSETOPPMSData.eto_channels, eto_channel)
            # elif self.software.startswith("ACTRANSPORT"):
            #     map_data = [key for key in data_df.keys() if 'Map' in key]
            #     if map_data:
            #         for key in map_data:
            #             map = CPFSACTData()
            #             if hasattr(map, 'name'):
            #                 setattr(map, 'name', key)
            #             if hasattr(map, 'map'):
            #                 setattr(map, 'map', data_df[key])
            #             self.data.m_add_sub_section(CPFSACTPPMSData.map_data, map)


m_package.__init_metainfo__()