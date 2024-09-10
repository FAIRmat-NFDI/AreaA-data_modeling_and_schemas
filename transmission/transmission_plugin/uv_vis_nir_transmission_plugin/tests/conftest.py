import glob
import logging
import os

import pytest
import structlog
from nomad.client import parse
from nomad.utils import structlogging
from structlog.testing import LogCapture

structlogging.ConsoleFormatter.short_format = True
setattr(logging, 'Formatter', structlogging.ConsoleFormatter)
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


@pytest.fixture(
    name='caplog',
    scope='function',
)
def fixture_caplog(request):
    """
    Extracts log messages from the logger and raises an assertion error if the specified
    log levels in the `request.param` are found.
    """
    caplog = LogCapture()
    processors = structlog.get_config()['processors']
    old_processors = processors.copy()

    try:
        processors.clear()
        processors.append(caplog)
        structlog.configure(processors=processors)
        yield caplog
        for record in caplog.entries:
            if record['log_level'] in request.param:
                assert False, record
    finally:
        processors.clear()
        processors.extend(old_processors)
        structlog.configure(processors=processors)
