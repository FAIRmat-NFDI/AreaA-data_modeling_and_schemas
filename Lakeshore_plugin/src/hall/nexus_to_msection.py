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
import numpy as np
from typing import Generator, Tuple, Optional
import re

from . import hall_instrument

from nomad.units import ureg

from .measurement import (
    Measurement,
    VariableTemperatureMeasurement,
    VariableTemperatureData,
    VariableFieldMeasurement,
    VariableFieldData,
    IVCurveMeasurement,
    IVData
)


def clean(unit: str) -> str:
    """Cleans an unit string, e.g. converts `VS` to `volt * seconds`.
    If the unit is not in the conversion dict the input string is
    returned without modification.

    Args:
        unit (str): The dirty unit string.

    Returns:
        str: The cleaned unit string.
    """
    conversions = {
        'VS': "volt * second",
        'Sec': "s",
        '²': "^2",
        '³': "^3",
        'ohm cm': "ohm * cm",
    }

    for old, new in conversions.items():
        unit = unit.replace(old, new)

    return unit


def get_measurement_object(measurement_type: str) -> Measurement:
    '''
    Gets a measurement MSection object from the given measurement type.

    Args:
        measurement_type (str): The measurement type.

    Returns:
        Measurement: A MSection representing a Hall measurement.
    '''
    if measurement_type == 'Variable Temperature Measurement':
        return VariableTemperatureMeasurement()
    if measurement_type == 'Variable Field Measurement':
        return VariableFieldMeasurement()
    if measurement_type == 'IV Curve Measurement':
        return IVCurveMeasurement()
    return Measurement()


def get_data_object(measurement_type: str):
    '''
    Gets a measurement data MSection object from the given measurement type.

    Args:
        measurement_type (str): The measurement type.

    Returns:
        A MSection representing a Hall measurement data object.
    '''
    if measurement_type == 'Variable Temperature Measurement':
        return VariableTemperatureData()
    if measurement_type == 'Variable Field Measurement':
        return VariableFieldData()
    if measurement_type == 'IV Curve Measurement':
        return IVData()
    return None


def to_snake_case(string: str) -> str:
    """
    Convert a string to snake_case.

    Preserve all non-alphanumeric characters but dashes,
    keep not separated capitalized acronyms,
    keep not separated multi-digit numbers

    Parameters:
        string (str): The string to convert.

    Returns:
        str: The converted string in snake_case.

    Example:
        >>> to_snake_case('My_String-Dashed_LS56 Sep AC / test_ls58_/@with_unit 345')
        'my_string_dashed_ls56_sep_ac/test_ls58/@with_unit_345'
    """

    string = string.replace('-', '_')
    string = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', '_', string)
    string = string.lower()
    string = re.sub(r'_{2,}', '_', string)
    string = re.sub(r'\b\d+\b', lambda match: match.group(0).replace('.', '_'), string)
    string = re.sub(r'\b(?<!\d)[A-Z]{2,}(?!\w)', lambda match: match.group(0).lower(), string)
    string = string.replace(' ', '_')
    string = re.sub(r'(?<=/)_', '', string)
    string = re.sub(r'_(?=/)', '', string)
    string = re.sub(r'_{2,}', '_', string)

    return string


def split_value_unit(expr: str) -> Tuple[str, Optional[str]]:
    '''
    Searches for a value unit pair and returns the values for a combination
    `value [unit]`.

    Args:
        expr (str): The expression to search for a value unit pair.

    Returns:
        Tuple[str, Optional[str]]:
            A tuple of value and unit.
            Returns the expr, where spaces are replaced with `_` and None when no
            value unit expression is found.
    '''
    is_value_unit = re.search(r'([^\[]+)\s\[(.*)\]', expr)
    if is_value_unit:
        value = to_snake_case(is_value_unit.group(1))
        unit = is_value_unit.group(2)
        return value.lower(), clean(unit)
    return to_snake_case(expr), None


def rename_key(key: str) -> str:
    '''
    Renames the key from the file to the eln

    Args:
        key (str): They key as read from the file.

    Returns:
        str: The key replaced with its eln counterpart
    '''
    key_map = {
        'use_zero_field_resistivity_to_calculate_hall_mobility':
            'use_zero_field_resistivity',
        'at_field': 'field_at_zero_resistivity',
        'at_temperature': 'temperature_at_zero_resistivity'
    }
    return key_map.get(key, key)


def calc_best_fit_values(iv_measurement: IVData) -> IVData:
    '''
    Calculates the best fit voltage values from the provided
    fitting data.

    Args:
        iv_measurement (IVData): The IVData without discrete best fit values.

    Returns:
        IVData: The IVdata with discret best fit values
    '''
    iv_measurement.best_fit_values = (
        iv_measurement.current * iv_measurement.best_fit_resistance
        + iv_measurement.best_fit_offset
    )

    return iv_measurement


def get_measurements(data_template: dict) -> Generator[Measurement, None, None]:
    '''
    Returns a hall measurement MSection representation form its corresponding
    nexus data_template.

    Args:
        data_template (dict): The nomad-parser-nexus data template.

    Yields:
        Generator[Measurement, None, None]:
            A generator yielding the single hall measurements.
    '''
    highest_index = 1

    for key in data_template:
        if bool(re.search(f'^/entry/measurement/{highest_index}_.+/', key)):
            highest_index += 1

    for measurement_index in range(1, highest_index):
        first = True
        data_entries: dict = {}
        contact_sets: dict = {}

        for key in data_template:
            if not key.startswith(f'/entry/measurement/{measurement_index}_'):
                continue

            if first:
                measurement_type = re.search(
                    f'measurement/{measurement_index}_([^/]+)/', key
                ).group(1)
                first = False
                eln_measurement = get_measurement_object(measurement_type)

            clean_key = to_snake_case(key.split(f'{measurement_type}/')[1])

            regexp = re.compile('/data(\\d+)/')
            if bool(regexp.search(key)):
                data_index = regexp.search(key).group(1)
                if data_index not in data_entries:
                    data_entries[data_index] = get_data_object(measurement_type)
                clean_dkey = clean_key.split(f'data{data_index}/')[1]
                if hasattr(data_entries[data_index], clean_dkey):
                    if f'{key}/@units' in data_template:
                        setattr(
                            data_entries[data_index],
                            clean_dkey,
                            data_template[key].astype(np.float64) * ureg(data_template[f'{key}/@units'])
                        )
                    else:
                        setattr(data_entries[data_index], clean_dkey, data_template[key])
                continue

            if '/Contact Sets/' in key:
                contact_set = re.search('/Contact Sets/([^/]+)/', key).group(1)
                if contact_set not in contact_sets:
                    contact_sets[contact_set] = get_data_object(measurement_type)
                clean_dkey = clean_key.split(f'{contact_set.lower()}/')[1]
                contact_sets[contact_set].contact_set = contact_set

                if 'data0' in key:
                    data = data_template[key]

                    for column in data.columns:
                        if (data[column] == 'ERROR').all():
                            continue
                        col, unit = split_value_unit(column)
                        clean_col = col.lower().replace(' ', '_')
                        if hasattr(contact_sets[contact_set], clean_col):
                            if unit is not None:
                                setattr(
                                    contact_sets[contact_set],
                                    clean_col,
                                    data[column].astype(np.float64) * ureg(unit)
                                )
                            else:
                                setattr(
                                    contact_sets[contact_set], clean_col, data[column]
                                )
                    continue

                clean_dkey, unit = split_value_unit(key.split(f'{contact_set}/')[1])
                if hasattr(contact_sets[contact_set], clean_dkey):
                    if unit is not None:
                        setattr(
                            contact_sets[contact_set],
                            clean_dkey,
                            data_template[key] * ureg(unit)
                        )
                    elif f'{key}/@units' in data_template:
                        setattr(
                            contact_sets[contact_set],
                            clean_dkey,
                            data_template[key] * ureg(data_template[f'{key}/@units'])
                        )
                    else:
                        setattr(
                            contact_sets[contact_set], clean_dkey, data_template[key]
                        )
                continue

            clean_key, unit = split_value_unit(key.split(f'{measurement_type}/')[1])
            clean_key = rename_key(clean_key)
            if hasattr(eln_measurement, clean_key):
                if f'{key}/@units' in data_template:
                    setattr(
                        eln_measurement,
                        clean_key,
                        data_template[key] * ureg(data_template[f'{key}/@units'])
                    )
                elif unit is not None:
                    if data_template[key] == 'ERROR':
                        continue
                    setattr(
                        eln_measurement,
                        clean_key,
                        data_template[key] * ureg(unit)
                    )
                else:
                    setattr(eln_measurement, clean_key, data_template[key])

        eln_measurement.data = []
        for data_entry in data_entries.values():
            eln_measurement.data.append(data_entry)

        for data_entry in contact_sets.values():
            eln_measurement.contact_sets.append(calc_best_fit_values(data_entry))

        yield eln_measurement


def instantiate_keithley(instrument, field_key, value, logger):
    '''
    Create an instance of a Keithley component class.

    The class is choosen among the available ones in hall_instrument module,
    based on which value is found in the `measurement_state_machine` section.
    '''

    subsection_key = field_key.replace('_', '')
    subsection_value = value.replace(' ', '')
    for attr_name, attr_class in vars(hall_instrument).items():
        if to_snake_case(subsection_value) in to_snake_case(attr_name):
            logger.info(f"The {field_key} is {value}")
            if not hasattr(instrument, subsection_key):
                logger.warn(f"{subsection_key} subsection not found")
            setattr(instrument, subsection_key, attr_class())
            return to_snake_case(value)


def get_instrument(data_template: dict, logger):
    '''
    Returns a hall instrument MSection representation form its corresponding
    nexus data_template.

    Args:
        data_template (dict): The nomad-parser-nexus data template.

    Yields:
        an Instrument object according to the schema in hall_instrument.py
    '''

    keithley_devices = ['electro_meter',
                        'volt_meter',
                        'current_meter',
                        'current_source'
                        ]
    keithley_components = {}
    other_components = ['system_parameters',
                        'temperature_controller',
                        'field_controller'
                        ]
    instrument = hall_instrument.Instrument()
    instrument.temperature_controller = hall_instrument.TemperatureController()
    instrument.field_controller = hall_instrument.FieldController()
    temperature_domains: dict = {}
    for key in data_template:
        clean_key = to_snake_case(key)
        field_key = clean_key.split('/')[-1]
        value = data_template[key]
        if "/measurement_state_machine/" in clean_key:
            if hasattr(instrument, field_key):
                setattr(instrument, field_key, value)
                for k_device in keithley_devices:
                    if k_device == clean_key.split('/measurement_state_machine/')[1]:
                        keithley_components[k_device.replace('_', '')
                                            ] = instantiate_keithley(instrument,
                                                                     field_key,
                                                                     value,
                                                                     logger)
        regexp = re.compile('temperature_domain_(\\d+)/')
        if bool(regexp.search(clean_key)):
            data_index = regexp.search(clean_key).group(1)
            if data_index not in temperature_domains:
                temperature_domains[data_index] = hall_instrument.TemperatureDomain()
            if hasattr(temperature_domains[data_index], field_key):
                setattr(temperature_domains[data_index], field_key, value)
            continue
        for instrument_comp in other_components:
            if instrument_comp is not None and f"/{instrument_comp}/" in clean_key:
                if hasattr(instrument, field_key):
                    setattr(instrument, field_key, value)
                elif hasattr(instrument, instrument_comp):
                    if hasattr(getattr(instrument, instrument_comp), field_key):
                        setattr(getattr(instrument, instrument_comp), field_key, value)
        for instrument_comp in list(keithley_components.keys()):
            if instrument_comp is not None and f"/{keithley_components[instrument_comp]}/" in clean_key:
                if hasattr(instrument, instrument_comp) and \
                    hasattr(getattr(instrument, instrument_comp),
                            field_key):
                    setattr(getattr(instrument, instrument_comp),
                            field_key, value)
    for t_domain in temperature_domains.values():
        instrument.m_add_sub_section(hall_instrument.Instrument.temperature_domain, t_domain)
    #print(f"{keithley_components}")
    #print(f"{list(keithley_components.keys())}")
    return instrument
