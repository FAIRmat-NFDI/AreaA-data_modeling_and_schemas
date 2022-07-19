"""This file reads an Hall ASCII measurement file into a dict"""
from typing import TextIO
import re
import pandas as pd
import numpy as np

# Replacement dict for section names
SECTION_REPLACEMENTS = {
    "Sample parameters": "entry/sample",
    "Measurements": "entry/measurement",
}

# Replacement dict for measurement indicators
MEASUREMENT_REPLACEMENTS = {
    "IV Curve Measurement": "iv_curve",
    "Variable Field Measurement": "variable_field",
}

# Keys that indicate the start of measurement block
MEASUREMENT_KEYS = ["Contact Sets"]


def is_section(expr: str) -> bool:
    """Checks whether an expression follows the form of a section
    i.e. is of the form [section]

    Args:
        expr (str): The current expression to check

    Returns:
        bool: Returns true if the expr is of the form of a section
    """
    return bool(re.search(r"^\[.+\]$", expr))


def is_measurement(expr):
    """Checks whether an expression follows the form of a measurement indicator
    i.e. is of the form <measurement>

    Args:
        expr (str): The current expression to check

    Returns:
        bool: Returns true if the expr is of the form of a measurement indicator
    """
    return bool(re.search(r"^\<.+\>$", expr))


def is_key(expr: str) -> bool:
    """Checks whether an expression follows the form of a key value pair
    i.e. is of the form key: value or key = value

    Args:
        expr (str): The current expression to check

    Returns:
        bool: Returns true if the expr is of the form of a key value pair
    """
    return bool(re.search(r"^.+\s*[:|=]\s*.+$", expr))


def is_meas_header(expr: str) -> bool:
    """Checks whether an expression follows the form of a measurement header,
    i.e. starts with: Word [Unit]

    Args:
        expr (str): The current expression to check

    Returns:
        bool: Returns true if the expr is of the form of a measurement header
    """
    return bool(re.search(r"^[^\]]+\[[^\]]+\]", expr))


def get_unique_dkey(dic: dict, dkey: str) -> str:
    """Checks whether a data key is already contained in a dictionary
    and returns a unique key if it is not.

    Args:
        dic (dict): The dictionary to check for keys
        dkey (str): The data key which shall be written.

    Returns:
        str: A unique data key. If a key already exists it is appended with a number
    """
    suffix = 0
    while f"{dkey}{suffix}" in dic:
        suffix += 1

    return f"{dkey}{suffix}"


def split_add_key(fobj: TextIO, dic: dict, prefix: str, expr: str) -> None:
    """_summary_

    Args:
        fobj (TextIO): The file object to read from
        dic (dict): The dict to write the data into
        prefix (str): Key prefix for the dict
        expr (str): The current expr/line to parse
    """
    key, *val = re.split(r"\s*[:|=]\s*", expr)
    jval = "".join(val).strip()

    if key in MEASUREMENT_KEYS:
        data = []
        for line in fobj:
            if not line.strip():
                break
            if is_key(line):
                split_add_key(
                    None,  # There should be no deeper measurement, prevent further consum of lines
                    dic,
                    f"{prefix}/{key}/{jval}",
                    line,
                )
            else:
                data.append(list(map(lambda x: x.strip(), re.split("\t+", line))))

        dkey = get_unique_dkey(dic, f"{prefix}/{key}/{jval}/data")
        dic[dkey] = pd.DataFrame(np.array(data[1:], dtype=np.float64), columns=data[0])
    else:
        dic[f"{prefix}/{key}"] = jval


def read_template_from_file(fname: str, encoding: str = "iso-8859-1") -> dict:
    """Reads a template dictonary from a hall measurement file

    Args:
        fname (str): The file name of the masurement file
        encoding (str, optional): The encoding of the ASCII file. Defaults to "iso-8859-1".

    Returns:
        dict: Dict containing the data and metadata of the measurement
    """
    template = {}
    current_section = "/entry"
    current_measurement = ""
    with open(fname, encoding=encoding) as fobj:
        for line in fobj:
            if is_section(line):
                sline = line.strip()[1:-1]
                current_section = f"/{SECTION_REPLACEMENTS.get(sline, sline)}"
                current_measurement = ""
            elif is_measurement(line):
                step, _, *meas = line.partition(":")
                sline = f"{step[6:]}_" + "".join(meas).strip()[:-1]
                current_measurement = f"/{MEASUREMENT_REPLACEMENTS.get(sline, sline)}"
            elif is_key(line):
                split_add_key(
                    fobj, template, f"{current_section}{current_measurement}", line
                )
            elif is_meas_header(line):
                data = []
                for mline in fobj:
                    if not mline.strip():
                        break
                    data.append(list(map(lambda x: x.strip(), re.split("\t+", mline))))

                header = list(map(lambda x: x.strip(), re.split("\t+", line)))
                dkey = get_unique_dkey(
                    template, f"{current_section}{current_measurement}/data"
                )
                template[dkey] = pd.DataFrame(
                    np.array(data, dtype=np.float64), columns=header
                )

    return template


def main() -> None:
    """Reads the example hall file and generates the template"""
    read_template_from_file("22-127-G_Hall-RT_TT-Halter.txt")
    read_template_from_file("22-127-G_20K-320K_TT-Halter_WDH_060722.txt")


if __name__ == "__main__":
    main()
