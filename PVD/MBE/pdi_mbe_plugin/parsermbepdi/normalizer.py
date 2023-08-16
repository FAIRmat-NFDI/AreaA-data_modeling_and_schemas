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
import glob

def epiclog_read(date, data_path, resampling_period):
    '''
    Function to modify the original log files from the custom Molecular
    Beam Epitaxy program EPIC, which is used in Paul-Drude-Institut.
    Produces pandas DataFrame for each text file, with index as a timestamp.
    '''
    path_list = [glob.glob(e) for e in [data_path + date + '/*.txt']][0]
    dataframe_list = [None] * len(path_list)

    for i in range(len(dataframe_list)):
        dataframe_list[i] = pd.read_csv(path_list[i], skiprows=1)
        dataframe_list[i].columns=dataframe_list[i].columns.str.replace('[\', #]','', regex=True)
        dataframe_list[i].comment = open(path_list[i],'r').readlines()[0][1:]
        dataframe_list[i].name = path_list[i][16:-4]

        # converting columns named as 'Date' and 'Date&Time' to timestamps
        # to merge single DataFrames as one.
        if 'Date&Time' in dataframe_list[i].columns:
            dataframe_list[i] = dataframe_list[i].rename({'Date&Time' : 'Date'}, axis='columns')

        dataframe_list[i].Date = pd.to_datetime(dataframe_list[i].Date, dayfirst=True)

        # rather than numerical index, timestamp index as resampling requires DateTimeIndex
        dataframe_list[i].index = dataframe_list[i]['Date']
        dataframe_list[i] = dataframe_list[i].drop(columns='Date')
        # resample to reduce the size of data arrays,
        # otherwise the dataframe combined becomes too big for the memory.
        if dataframe_list[i].columns.size == 3:
            agg_rules = { "CallerID" : "last","Message" : "last", "Color" : "last"}
            dataframe_list[i] = dataframe_list[i].resample(resampling_period).agg(agg_rules)
        elif dataframe_list[i].columns.size == 11:
            dataframe_list[i] = dataframe_list[i].resample(resampling_period).last()
        else:
            dataframe_list[i] = dataframe_list[i].resample(resampling_period).mean()
    return dataframe_list

def epicdf_combine(dataframe_list):
    '''
    This function is used to combine the imported log DataFrames to a single DataFrame
    '''
    single_df = dataframe_list[0]
    for i in range(len(dataframe_list[1:])):
        single_df = pd.merge(single_df, dataframe_list[1:][i], on='Date', how='outer')

    return single_df

def epic_xlsx(date, data_path, single_df):
    '''
    Export DataFrame as *.xlsx file.
    '''
    with pd.ExcelWriter(data_path + 'mbe_data_' + date + '.xlsx') as writer:
        single_df.to_excel(writer)

    return print('file successfully exported')