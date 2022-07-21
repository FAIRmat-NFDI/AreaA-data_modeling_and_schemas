"""Functions to read perkin ellmer transmission files"""
from typing import Tuple
import pandas as pd


def read_asc(fname: str, encoding: str = "utf-8") -> Tuple[list, pd.DataFrame]:
    """Reads perkin ellmer asc transmission files

    Args:
        fname (str): Filename of the asc file
        encoding (str, optional): Encoding of the file. Defaults to "utf-8".

    Returns:
        Tuple[list, pd.DataFrame]: List of header lines and DataFrame of the data
    """
    # This value indicates that the data block is starting
    data_start_ind = "#DATA"

    with open(fname, encoding=encoding) as fobj:
        keys = []
        for line in fobj:
            if line.strip() == data_start_ind:
                break
            keys.append(line.strip())

        transmission_data = pd.read_csv(
            fobj, delim_whitespace=True, header=None, index_col=0
        )

    return keys, transmission_data
