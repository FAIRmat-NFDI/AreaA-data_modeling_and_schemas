import pytest
from glob import glob
from nomad.client import parse, normalize_all
import Lakeshore

def get_test_files():
    """Get the transformation example file path."""
    return glob("tests/data/*.dat")


# @pytest.mark.parametrize('filename', get_test_files())
# def test_file_parsing(filename):
#     Lakeshore.reader.parse_txt(filename)


# @pytest.mark.parametrize('filename', get_test_files())
# def test_msection_generation(filename):
#     data_template = Lakeshore.reader.parse_txt(filename)
#     list(Lakeshore.nexus_to_msection.get_measurements(data_template))

@pytest.mark.parametrize('test_file', glob('tests/data/testPPMS.dat'))
def test_schema(test_file):
    entry_archive = parse(test_file)[0]
    normalize_all(entry_archive)