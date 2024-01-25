import pytest
from glob import glob
from nomad.client import parse, normalize_all
import hall

def get_test_files():
    """Get the transformation example file path."""
    return glob("tests/data/*.txt")


@pytest.mark.parametrize('filename', get_test_files())
def test_file_parsing(filename):
    hall.reader.parse_txt(filename)


@pytest.mark.parametrize('filename', get_test_files())
def test_msection_generation(filename):
    data_template = hall.reader.parse_txt(filename)
    list(hall.nexus_to_msection.get_measurements(data_template))

@pytest.mark.parametrize('test_file', glob('tests/data/hall_eln_*.archive.yaml'))
def test_schema(test_file):
    entry_archive = parse(test_file)[0]
    normalize_all(entry_archive)