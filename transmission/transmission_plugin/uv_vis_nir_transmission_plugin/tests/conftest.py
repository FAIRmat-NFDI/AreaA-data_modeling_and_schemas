import os
import glob
import pytest
from nomad.client import parse

test_files = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*.asc'))


@pytest.fixture(params=test_files)
def parsed_archive(request):
    """
    Sets up data for testing and cleans up after the test.
    """
    rel_file = os.path.join('tests', 'data', request.param)
    file_archive = parse(rel_file)[0]
    measurement = os.path.join(
        'tests', 'data', '.'.join(request.param.split('.')[:-1]) + '.archive.json'
    )
    assert file_archive.data.measurement.m_proxy_value == os.path.abspath(measurement)
    measurement_archive = parse(measurement)[0]

    yield measurement_archive

    if os.path.exists(measurement):
        os.remove(measurement)
