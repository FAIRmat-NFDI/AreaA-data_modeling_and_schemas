"""Lake Shore Hall file reader implementation for the DataConverter."""
from pathlib import Path
import re
from typing import Any, List, TextIO, Dict, Optional
import logging
import numpy as np
import pandas as pd

from typing import Tuple, Any, Callable, Dict, List
import os

from abc import ABC, abstractmethod

from . import helpers
from . import utils


class BaseReader(ABC):
    """
    The abstract class off of which to implement readers.

    The filename's prefix is the identifier. The '_reader.py' is snipped out.
    For this BaseReader with filename base_reader.py the ID  becomes 'base'

    For future reference:
    - Support links by setting the path in the template with the following object
       object = {"link": "/path/to/source/data"}
    """

    # pylint: disable=too-few-public-methods

    __name__ = "BaseReader"

    # Whitelist for the NXDLs that the reader supports and can process
    supported_nxdls = [""]

    @abstractmethod
    def read(self,
             template: dict = None,
             file_paths: Tuple[str] = None,
             objects: Tuple[Any] = None) -> dict:
        """Reads data from given file and returns a filled template dictionary"""
        return template


class YamlJsonReader(BaseReader):
    """A reader that takes a mapping json file and a data file/object to return a template."""

    # pylint: disable=too-few-public-methods

    # Whitelist for the NXDLs that the reader supports and can process
    supported_nxdls: List[str] = []
    extensions: Dict[str, Callable[[str], dict]] = {}

    def read(self,
             template: dict = None,
             file_paths: Tuple[str] = None,
             _: Tuple[Any] = None) -> dict:
        """
        Reads data from multiple files and passes them to the appropriate functions
        in the extensions dict.
        """

        sorted_paths = sorted(file_paths, key=lambda f: os.path.splitext(f)[1])
        for file_path in sorted_paths:
            extension = os.path.splitext(file_path)[1]
            if extension not in self.extensions:
                print(
                    f"WARNING: "
                    f"File {file_path} has an unsupported extension, ignoring file."
                )
                continue
            if not os.path.exists(file_path):
                print(f"WARNING: File {file_path} does not exist, ignoring entry.")
                continue

            template.update(self.extensions.get(extension, lambda _: {})(file_path))

        template.update(self.extensions.get("default", lambda _: {})(""))

        return template



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

# Dict for converting values for specific keys
CONVERSION_FUNCTIONS = {
    "Start Time": helpers.convert_date,
    "Time Completed": helpers.convert_date,
    "Skipped at": helpers.convert_date
}

# Keys that indicate the start of measurement block
MEASUREMENT_KEYS = ["Contact Sets"]

reader_dir = Path(__file__).parent
config_file = reader_dir.joinpath("enum_map.json")
ENUM_FIELDS = utils.parse_json(str(config_file))

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


def split_add_key(fobj: Optional[TextIO], dic: dict, prefix: str, expr: str) -> None:
    """Splits a key value pair and adds it to the dictionary.
    It also checks for measurement headers and adds the full tabular data as a
    pandas array to the dictionary.

    Args:
        fobj (TextIO): The file object to read from
        dic (dict): The dict to write the data into
        prefix (str): Key prefix for the dict
        expr (str): The current expr/line to parse
    """
    key, *val = re.split(r"\s*[:|=]\s*", expr)
    jval = "".join(val).strip()

    def parse_enum() -> bool:
        sprefix = prefix.strip("/")
        if 'Keithley' not in sprefix:
            w_trailing_num = re.search(r"(.*) \d+$", sprefix)
            if w_trailing_num:
                sprefix = w_trailing_num.group(1)

        if (
            sprefix in ENUM_FIELDS
            and key in ENUM_FIELDS[sprefix]
            and helpers.is_integer(jval)
        ):
            if jval not in ENUM_FIELDS[sprefix][key]:
                logger.warning("Option `%s` not in `%s, %s`", jval, sprefix, key)
            dic[f"{prefix}/{key}"] = ENUM_FIELDS[sprefix][key].get(jval, "UNKNOWN")
            return True

        return False

    def parse_field():
        if helpers.is_value_with_unit(jval):
            value, unit = helpers.split_value_with_unit(jval)
            dic[f"{prefix}/{key}"] = value
            dic[f"{prefix}/{key}/@units"] = helpers.clean(unit)
            return

        if parse_enum():
            return

        if helpers.is_integer(jval):
            dic[f"{prefix}/{key}"] = int(jval)
            return

        if helpers.is_number(jval):
            dic[f"{prefix}/{key}"] = float(jval)
            return

        if helpers.is_boolean(jval):
            dic[f"{prefix}/{key}"] = helpers.to_bool(jval)
            return

        dic[f"{prefix}/{key}"] = CONVERSION_FUNCTIONS.get(key, lambda v: v)(jval)

    def parse_data():
        data = []
        for line in fobj:
            if not line.strip():
                break
            if helpers.is_key(line):
                split_add_key(
                    None,  # There should be no deeper measurement,
                    # prevent further consumption of lines
                    dic,
                    f"{prefix}/{key}/{jval}",
                    line,
                )
                continue
            data.append(list(map(lambda x: x.strip(), re.split("\t+", line))))

        dkey = helpers.get_unique_dkey(dic, f"{prefix}/{key}/{jval}/data")
        dic[dkey] = pd.DataFrame(
            np.array(data[1:]), columns=data[0]
        ).apply(pd.to_numeric, args=('coerce',))

    if fobj is not None and key in MEASUREMENT_KEYS:
        parse_data()
    else:
        parse_field()


def parse_txt(fname: str, encoding: str = "iso-8859-1") -> dict:
    """Reads a template dictonary from a hall measurement file

    Args:
        fname (str): The file name of the masurement file
        encoding (str, optional): The encoding of the ASCII file. Defaults to "iso-8859-1".

    Returns:
        dict: Dict containing the data and metadata of the measurement
    """
    def parse_measurement(line_number: int, line: str, current_section: str, current_measurement: str):
        data = []
        nested_line_number = 0
        for mline in fobj:
            nested_line_number += 1
            print(f"LINE {line_number + nested_line_number}: DATA. {mline}")
            if not mline.strip():
                break
            data.append(list(map(lambda x: x.strip(), re.split("\t+", mline))))

        header = list(map(lambda x: x.strip(), re.split("\t+", line)))
        dkey = helpers.get_unique_dkey(
            template, f"{current_section}{current_measurement}/data"
        )
        template.update(helpers.pandas_df_to_template(
            dkey,
            pd.DataFrame(
                #np.array(data, dtype=np.float64), columns=header # !! type check skipped
                np.array(data), columns=header
            ).apply(pd.to_numeric, args=('coerce',))
        ))

        return current_section, current_measurement, nested_line_number

    def parse(line_number: int, line: str, current_section: str, current_measurement: str):
        if helpers.is_section(line):
            print(f"LINE {line_number}: SECTION. {line}")
            sline = line.strip()[1:-1]
            current_section = f"/{SECTION_REPLACEMENTS.get(sline, sline)}"
            current_measurement = ""
            return current_section, current_measurement, 0

        if helpers.is_measurement(line):
            print(f"LINE {line_number}: MEASUREMENT. {line}")
            step, _, *meas = line.partition(":")
            sline = f"{step[6:]}_" + "".join(meas).strip()[:-1]
            current_measurement = f"/{MEASUREMENT_REPLACEMENTS.get(sline, sline)}"
            return current_section, current_measurement, 0

        if helpers.is_key(line):
            print(f"LINE {line_number}: KEY. {line}")
            split_add_key(
                fobj, template, f"{current_section}{current_measurement}", line
            )
            return current_section, current_measurement, 0

        if helpers.is_meas_header(line):
            print(f"LINE {line_number}: MEAS HEADER. {line}")
            return parse_measurement(line_number, line, current_section, current_measurement)

        print(f"LINE {line_number}: NO OTHER OPTION. {line}")
        if line.strip():
            logger.warning("Line `%s` ignored", line.strip())

        return current_section, current_measurement, 0

    template: Dict[str, Any] = {}
    current_section = "/entry"
    current_measurement = ""
    with open(fname, encoding=encoding) as fobj:
        tot_line_number = 0
        nested_line_number = 0
        for line_number, line in enumerate(fobj, start=1):
            tot_line_number = line_number + nested_line_number
            current_section, current_measurement, nested_ln = parse(
                tot_line_number, line, current_section, current_measurement
            )
            nested_line_number += nested_ln

    return template
