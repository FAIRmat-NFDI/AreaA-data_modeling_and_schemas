import pytest
from nomad.units import ureg
from transmission.readers import (
    read_sample_name,
    read_start_datetime,
    read_attenuation_percentage,
    read_long_line,
)


@pytest.mark.parametrize(
    'param, expected',
    [
        ([''], {'sample': None, 'reference': None}),
        (['S:100'], {'sample': 100, 'reference': None}),
        (['R:100'], {'sample': None, 'reference': 100}),
        (['S:100 R:100'], {'sample': 100, 'reference': 100}),
        (['S: R:100'], {'sample': None, 'reference': 100}),
        (['3350/S: 3350/R:100'], {'sample': None, 'reference': 100}),
    ],
)
def test_read_attenuation_percentage(param, expected):
    param_list = ['' for i in range(47)]
    param_list.extend(param)
    assert read_attenuation_percentage(param_list, logger=None) == expected


@pytest.mark.parametrize(
    'param, expected',
    [
        ([''], None),
        (['sample'], 'sample'),
        (['sample.txt'], 'sample'),
        (['sample.txt.txt'], 'sample'),
    ],
)
def test_read_sample_name(param, expected):
    param_list = ['' for i in range(2)]
    param_list.extend(param)
    assert read_sample_name(param_list, logger=None) == expected


@pytest.mark.parametrize(
    'param, expected',
    [
        (['', ''], None),
        (['19/06/25', '11:03:40.00'], '2019-06-25T11:03:40.00Z'),
    ],
)
def test_read_start_datetime(param, expected):
    param_list = ['' for i in range(3)]
    param_list.extend(param)
    assert read_start_datetime(param_list, logger=None) == expected


@pytest.mark.parametrize(
    'param, expected',
    [
        (
            '3350/2.4 860.8/2.05',
            [
                {'wavelength': 3350 * ureg.nm, 'value': 2.4},
                {'wavelength': 860.8 * ureg.nm, 'value': 2.05},
            ],
        ),
        (
            '2.4 860.8/2.05',
            [
                {'wavelength': None, 'value': 2.4},
                {'wavelength': 860.8 * ureg.nm, 'value': 2.05},
            ],
        ),
        (
            '2.4',
            [
                {'wavelength': None, 'value': 2.4},
            ],
        ),
    ],
)
def test_read_long_line(param, expected):
    assert read_long_line(param, logger=None) == expected
