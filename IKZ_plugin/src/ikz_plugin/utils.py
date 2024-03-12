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

import re
import yaml
import json
import math
import pandas as pd
from typing import List


def get_reference(upload_id, entry_id):
    return f"../uploads/{upload_id}/archive/{entry_id}"


def get_entry_id_from_file_name(filename, upload_id):
    from nomad.utils import hash

    return hash(upload_id, filename)


def nan_equal(a, b):
    """
    Compare two values with NaN values.
    """
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    elif isinstance(a, dict) and isinstance(b, dict):
        return dict_nan_equal(a, b)
    elif isinstance(a, list) and isinstance(b, list):
        return list_nan_equal(a, b)
    else:
        return a == b


def list_nan_equal(list1, list2):
    """
    Compare two lists with NaN values.
    """
    if len(list1) != len(list2):
        return False
    for a, b in zip(list1, list2):
        if not nan_equal(a, b):
            return False
    return True


def dict_nan_equal(dict1, dict2):
    """
    Compare two dictionaries with NaN values.
    """
    if set(dict1.keys()) != set(dict2.keys()):
        return False
    for key in dict1:
        if not nan_equal(dict1[key], dict2[key]):
            return False
    return True


def create_archive(
    entry_dict, context, filename, file_type, logger, *, overwrite: bool = False
):
    from nomad.datamodel.context import ClientContext

    if isinstance(context, ClientContext):
        return None
    if context.raw_path_exists(filename):
        with context.raw_file(filename, "r") as file:
            existing_dict = yaml.safe_load(file)
    if context.raw_path_exists(filename) and not dict_nan_equal(
        existing_dict, entry_dict
    ):
        logger.error(
            f"{filename} archive file already exists. "
            f"You are trying to overwrite it with a different content. "
            f"To do so, remove the existing archive and click reprocess again."
        )
    if (
        not context.raw_path_exists(filename)
        or existing_dict == entry_dict
        or overwrite
    ):
        with context.raw_file(filename, "w") as newfile:
            if file_type == "json":
                json.dump(entry_dict, newfile)
            elif file_type == "yaml":
                yaml.dump(entry_dict, newfile)
        context.upload.process_updated_raw_file(filename, allow_modify=True)

    return get_reference(
        context.upload_id, get_entry_id_from_file_name(filename, context.upload_id)
    )


def row_to_array(
    dataframe: pd.DataFrame, quantities: List[str], row_index: int
) -> pd.Series:
    """take same name headers in a dataframe and return them as an array

    Args:
        dataframe (pd.DataFrame): data to be parsed
        quantities (List[str]): the repeating header names in the dataframe
        row_index (int): the index of the row to be parsed

    Returns:
        pd.Series: an array containing all the values of the same name headers repeated along one row
    """
    array = pd.Series([])
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in dataframe.columns
            for key in quantities
        ):
            array = array.append(
                pd.Series(
                    [
                        dataframe[
                            f"{quantities[0]}{'' if i == 0 else '.' + str(i)}"
                        ].loc[row_index],
                    ]
                )
            )
            i += 1
        else:
            break
    return array


def clean_dataframe_headers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Picks first row of a DataFrame and makes it as new headers.

    This function takes a DataFrame (without headers) as input and uses the first row as the new column names.
    It modifies these column names by removing trailing spaces and handling duplicate column names.
    Duplicate column names are handled by appending a count to the end of the column name.
    This functionality also a built-in in pandas, but it is not used here because it does not handle
    duplicate column names as expected.

    After setting the new column names, the function removes the first row (which has been used as headers)
    and resets the index.

    Args:
        dataframe (pd.DataFrame): The input DataFrame (without headers) whose first row is to be used as
        the new column names and then cleaned.

    Returns:
        pd.DataFrame: The modified DataFrame with cleaned column names, removed first row, and reset index.
    """

    # Create a dictionary to keep track of the count of each column name
    column_counts = {}
    # Create a list to store the new column names
    new_columns = []
    # Iterate over the columns
    for col in dataframe.iloc[0]:
        # Clean up the column name
        col = re.sub(r"\s+", " ", str(col).strip())
        # If the column name is in the dictionary, increment the count
        if col in column_counts:
            column_counts[col] += 1
        # Otherwise, add the column name to the dictionary with a count of 1
        else:
            column_counts[col] = 1
        # If the count is greater than 1, append it to the column name
        if column_counts[col] > 1:
            col = f"{col}.{column_counts[col] - 1}"
        # Add the column name to the list of new column names
        new_columns.append(col)
    # Assign the new column names to the DataFrame
    dataframe.columns = new_columns
    # Remove the first row (which contains the original headers)
    dataframe = dataframe.iloc[1:]
    # Reset the index
    dataframe = dataframe.reset_index(drop=True)

    return dataframe
