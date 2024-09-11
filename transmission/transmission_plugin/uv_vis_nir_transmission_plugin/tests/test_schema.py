import glob
import os.path

import pytest
from nomad.client import normalize_all, parse

test_files = glob.glob(os.path.join(os.path.dirname(__file__), 'data/stable_version/*'))


@pytest.mark.usefixtures('caplog')
@pytest.mark.parametrize(
    'caplog',
    ['error', 'critical'],
    indirect=True,
)
@pytest.mark.parametrize('test_file', test_files)
def test_backward_compatibility(test_file):
    entry_archive = parse(test_file)[0]
    normalize_all(entry_archive)
