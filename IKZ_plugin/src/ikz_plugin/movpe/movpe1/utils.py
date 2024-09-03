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

import pandas as pd


def create_timeseries_objects(
    dataframe: pd.DataFrame, quantities, MetainfoClass, index
):
    """_summary_

    Args:
        dataframe (pd.DataFrame): _description_
        quantities (_type_): _description_
        MetainfoClass (_type_): _description_
        index (_type_): _description_

    Returns:
        _type_: _description_
    """
    objects = []
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in dataframe.columns
            for key in quantities
        ):
            objects.append(
                MetainfoClass(
                    time=dataframe.get(
                        f"{quantities[0]}{'' if i == 0 else '.' + str(i)}", ''
                    )[index],
                    value=dataframe.get(
                        f"{quantities[1]}{'' if i == 0 else '.' + str(i)}", 0
                    )[index],
                )
            )
            i += 1
        else:
            break
    return objects
