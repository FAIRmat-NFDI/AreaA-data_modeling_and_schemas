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

import json
import math
import re

import pandas as pd
import yaml


def get_reference(upload_id, entry_id):
    return f'../uploads/{upload_id}/archive/{entry_id}'


def get_entry_id(upload_id, filename):
    from nomad.utils import hash

    return hash(upload_id, filename)


def get_hash_ref(upload_id, filename):
    return f'{get_reference(upload_id, get_entry_id(upload_id, filename))}#data'


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
        with context.raw_file(filename, 'r') as file:
            existing_dict = yaml.safe_load(file)
    if context.raw_path_exists(filename) and not dict_nan_equal(
        existing_dict, entry_dict
    ):
        logger.error(
            f'{filename} archive file already exists. '
            f'You are trying to overwrite it with a different content. '
            f'To do so, remove the existing archive and click reprocess again.'
        )
    if (
        not context.raw_path_exists(filename)
        or existing_dict == entry_dict
        or overwrite
    ):
        with context.raw_file(filename, 'w') as newfile:
            if file_type == 'json':
                json.dump(entry_dict, newfile)
            elif file_type == 'yaml':
                yaml.dump(entry_dict, newfile)
        context.upload.process_updated_raw_file(filename, allow_modify=True)

    return get_hash_ref(context.upload_id, filename)


def df_value(dataframe, column_header, index=None):
    """
    Fetches a value from a DataFrame.
    """
    if column_header in dataframe.columns:
        if index is not None:
            return dataframe[column_header][index]
        return dataframe[column_header]
    return None


def typed_df_value(dataframe, column_header, value_type, index=None):
    """
    Fetches a value of a specified type from a DataFrame.
    """
    value = df_value(dataframe, column_header, index)
    if value_type is str:
        return str(value)
    if isinstance(value, value_type):
        return value
    return None


def row_to_array(dataframe: pd.DataFrame, quantity: str, row_index: int) -> pd.Series:
    """
    Extracts values from a DataFrame row across multiple columns with similar names.

    This function takes a DataFrame, a list of header names, and a row index. It extracts
    the values from the specified row across all columns whose names start with any of the
    specified header names. The column names are expected to follow a specific pattern:
    the base header name, followed by a dot and an integer index (e.g., 'header.1', 'header.2', etc.).
    The function returns a Series containing all the extracted values.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing the data.
        quantities (List[str]): The base names of the headers. The DataFrame should contain
                                 multiple columns with names that start with each base name.
        row_index (int): The index of the row from which to extract the values.

    Returns:
        pd.Series: A Series containing all the values extracted from the specified row across
                   all columns with names that start with any of the specified header names.

    Example:
        >>> df = pd.DataFrame({
        ...     'header': [1, 2, 3],
        ...     'header.1': [4, 5, 6],
        ...     'header.2': [7, 8, 9]
        ... })
        >>> array = row_to_array(df, ['header'], 0)
        >>> print(array)
        0    1
        1    4
        2    7
        dtype: int64
    """
    column_names = [col for col in dataframe.columns if col.startswith(quantity)]
    array = pd.Series(
        [
            dataframe[col].loc[row_index]
            for col in column_names
            if isinstance(dataframe[col].loc[row_index], float)
            or isinstance(dataframe[col].loc[row_index], int)
        ]
    )
    return array


def clean_timeseries(time_array: pd.Series, value_array: pd.Series) -> pd.Series:
    """
    clean time and value array pairs by removing NaNs
    """
    # for i in time_array.index:
    #     if pd.isna(time_array.loc[i]).any() or pd.isna(value_array.loc[i]).any():
    #         time_array = time_array.drop(i)
    #         value_array = value_array.drop(i)
    # return time_array, value_array
    df = pd.concat([time_array, value_array], axis=1)
    df = df.dropna()
    return df.iloc[:, 1], df.iloc[:, 0]


def row_timeseries(
    dataframe: pd.DataFrame, time_header: str, value_header: str, row_index: int
) -> pd.Series:
    """
    Extracts and cleans a timeseries from a row of a DataFrame.

    This function takes a DataFrame, two header names (one for time and one for values),
    and a row index. It extracts the timeseries data from the specified row, where the
    time and value data are stored in columns with the specified header names. The function
    then cleans the extracted timeseries by removing any NaN values.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing the timeseries data.
        time_header (str): The header name for the time data. The DataFrame should contain
                            multiple columns with this header name, each containing a time point.
        value_header (str): The header name for the value data. The DataFrame should contain
                             multiple columns with this header name, each containing a value
                             corresponding to a time point.
        row_index (int): The index of the row from which to extract the timeseries.

    Returns:
        tuple: A tuple containing two pd.Series objects. The first Series contains the time
               points of the timeseries, and the second Series contains the corresponding values.
               Both Series have been cleaned to remove any NaN values.

    Example:
        >>> df = pd.DataFrame({
        ...     'time': [1, 2, 3],
        ...     'time.1': [4, 5, 6],
        ...     'value': [7, 8, 9],
        ...     'value.1': [10, 11, 12]
        ... })
        >>> time_series, value_series = row_timeseries(df, 'time', 'value', 0)
        >>> print(time_series)
        0    1
        1    4
        dtype: int64
        >>> print(value_series)
        0     7
        1    10
        dtype: int64
    """
    return clean_timeseries(
        row_to_array(
            dataframe,
            value_header,
            row_index,
        ),
        row_to_array(
            dataframe,
            time_header,
            row_index,
        ),
    )


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
        col = re.sub(r'\s+', ' ', str(col).strip())
        # If the column name is in the dictionary, increment the count
        if col in column_counts:
            column_counts[col] += 1
        # Otherwise, add the column name to the dictionary with a count of 1
        else:
            column_counts[col] = 1
        # If the count is greater than 1, append it to the column name
        if column_counts[col] > 1:
            col = f'{col}.{column_counts[col] - 1}'
        # Add the column name to the list of new column names
        new_columns.append(col)
    # Assign the new column names to the DataFrame
    dataframe.columns = new_columns
    # Remove the first row (which contains the original headers)
    dataframe = dataframe.iloc[1:]
    # Reset the index
    dataframe = dataframe.reset_index(drop=True)

    return dataframe
