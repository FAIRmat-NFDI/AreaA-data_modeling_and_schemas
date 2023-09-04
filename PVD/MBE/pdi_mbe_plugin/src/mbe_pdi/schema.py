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

# REPLACE dataframe_list[i] = dataframe_list[i].FUNC with (inplace=True) method!!

import pandas as pd
import glob

def epiclog_read(date, data_path, percent_cut, value_cut, resampling_period, resample_method = 'diff'):
    '''
    Function to modify the original log files from the custom Molecular
    Beam Epitaxy program EPIC, which is used in Paul-Drude-Institut.
    Produces pandas DataFrame for each text file, with index as a timestamp.
    This DataFrame are resampled either with time intervals or absolute(for temperature values)
    or relative(for pressure values) difference. Default is resampling by difference.
    '''
    path_list = [glob.glob(e) for e in [data_path + date + '/*.txt']][0]
    dataframe_list = [None] * len(path_list)

    for i in range(len(dataframe_list)):

        # Read log files
        dataframe_list[i] = pd.read_csv(path_list[i], skiprows=1)

        # Replace the unnecessary \` character in the beginning of files
        # Replace "."/dots with "_"
        dataframe_list[i].columns=dataframe_list[i].columns.str.replace('[\', #]','', regex=True)
        dataframe_list[i].columns=dataframe_list[i].columns.str.replace('[.]','-', regex=True)

        # converting columns named as 'Date' and 'Date&Time' to timestamps
        # It is useful when merging them as single *.xlsx file
        if 'Date&Time' in dataframe_list[i].columns:
            dataframe_list[i] = dataframe_list[i].rename({'Date&Time' : 'Date'}, axis='columns')

        dataframe_list[i].Date = pd.to_datetime(dataframe_list[i].Date, dayfirst=True)

        # rather than numerical index, timestamp index as resampling
        # by time requires DateTimeIndex
        dataframe_list[i].index = dataframe_list[i]['Date']
        dataframe_list[i] = dataframe_list[i].drop(columns='Date')
        
        #If initiate this attributes before resampling, they are deleted??
        dataframe_list[i].comment = open(path_list[i],'r').readlines()[0][1:]
        dataframe_list[i].name = path_list[i][16:-4]

        # Fill the empty rows of Shutter DataFrame
        if dataframe_list[i].name == "Shutters":
            dataframe_list[i].fillna(method='ffill', inplace=True)

        # Resampling, either over DateTime or Relative/Absolute Change
        if resample_method == 'diff':

            # Only resize data texts(Date and additional column),
            # effectively leave out Messages and Shutter out.
            if dataframe_list[i].columns.size < 3:
                # Search for pressure related log files and create new DataFrame by using 
                # relative change (dataframe.pct_change()\*100) to fill a newly created
                # DataFrame only with values over certain threshold percentages.
                # Search columns with the name inside 'IG', 'MIG' or 'PG' which gives
                # pressure related log data.
                if dataframe_list[i].filter(regex='IG|MIG|PG').columns.values.tolist():
                    # using pct_change to find relative difference between the following columns
                    # with pd.merge, merge the relative difference column and real value.
                    # set index to Date and delete the rows that are zero with
                    # .loc[(dataframe_list[i]!=0).any(axis=1)]
                    # if you want to drop the NaN value row (which, the first value will also be)
                    # add .dropna() to line just below.
                    dataframe_list[i] = pd.merge(dataframe_list[i].reset_index(), dataframe_list[i].pct_change().reset_index(), on=['Date']).set_index('Date').loc[(dataframe_list[i].pct_change()!=0).any(axis=1)]
                    # remove the rows only below certain percentage that user gives,
                    # using the additional column with relative difference values created above.
                    dataframe_list[i] = dataframe_list[i][dataframe_list[i].iloc[:, 1] > (percent_cut / 100 )]
                    # drop the column with relative differences after selection.
                    dataframe_list[i] = dataframe_list[i].drop(columns=dataframe_list[i].iloc[:,1:].columns.tolist())
                    # after the merge function, the data column and the difference column are named as
                    # NAME_x and NAME_y respectively, as difference column is dropped, there is no need
                    # to keep the _x suffix in the end NAME.
                    dataframe_list[i].columns = dataframe_list[i].columns.str.replace('[_x]','', regex=True)

                # Search for temperature related log files and create new DataFrame by using 
                # absolute change (dataframe.diff()) to fill a newly created DataFrame
                # only with values over certain threshold value. Search columns with the
                # name inside 'PID' or 'Pyro' which gives temperature related log data.
                if dataframe_list[i].filter(regex='PID|Pyro').columns.values.tolist():
                    # using diff to find absolute difference between the following columns
                    # with pd.merge, merge the relative difference column and real value.
                    # set index to Date and delete the rows that are zero with
                    # .loc[(dataframe_list[i]!=0).any(axis=1)]
                    # if you want to drop the NaN value row (which, the first value will also be)
                    # add .dropna() to line just below.
                    dataframe_list[i] = pd.merge(dataframe_list[i].reset_index(), dataframe_list[i].diff().reset_index(), on=['Date']).set_index('Date').loc[(dataframe_list[i].diff()!=0).any(axis=1)]
                    # remove the rows only below certain value that user gives,
                    # using the additional column with absolute difference values created above.
                    dataframe_list[i] = dataframe_list[i][dataframe_list[i].iloc[:, 1] > value_cut]
                    # drop the column with relative differences after selection.
                    dataframe_list[i] = dataframe_list[i].drop(columns=dataframe_list[i].iloc[:,1:].columns.tolist())
                    # after the merge function, the data column and the difference column are named as
                    # NAME_x and NAME_y respectively, as difference column is dropped, there is no need
                    # to keep the _x suffix in the end NAME.
                    dataframe_list[i].columns=dataframe_list[i].columns.str.replace('[_x]','', regex=True)
        else:
            # resample by time to reduce the size of data arrays,
            # otherwise the dataframe combined becomes too big for the memory.
            if dataframe_list[i].columns.size == 3:
                agg_rules = { "CallerID" : "last","Message" : "last", "Color" : "last"}
                dataframe_list[i] = dataframe_list[i].resample(resampling_period).agg(agg_rules)
            elif dataframe_list[i].columns.size == 11:
                dataframe_list[i] = dataframe_list[i].resample(resampling_period).last()
            else:
                dataframe_list[i] = dataframe_list[i].resample(resampling_period).mean()

        # have re-run this again, metadata is lost after df = df methods
        # must be replaced with (inplace=True) method.
        dataframe_list[i].comment = open(path_list[i],'r').readlines()[0][1:]
        dataframe_list[i].name = path_list[i][16:-4]

    return dataframe_list

def epic_xlsx(date, data_path, dataframe_list):
    '''
    Export DataFrame to single sheets in a single *.xlsx file
    '''
    with pd.ExcelWriter(data_path + 'mbe_data_' + date + '.xlsx') as writer:
        for i in range(len(dataframe_list)):
            dataframe_list[i].to_excel(writer, sheet_name=dataframe_list[i].name)

    return print('file successfully exported')

def epicdf_combine(dataframe_list):
    '''
    This function is used to combine the imported log DataFrames to a single DataFrame.
    '''
    single_df = dataframe_list[0]
    for i in range(len(dataframe_list[1:])):
        single_df = pd.merge(single_df, dataframe_list[1:][i], on='Date', how='outer')

    return single_df

def epic_xlsx_single(date, data_path, single_df):
    '''
    Export DataFrame as *.xlsx file. Must be used with the epicdf_combine function
    Sheet_name must be used with a string like 'epic_log_data',
    single_df.name does not work.
    '''
    with pd.ExcelWriter(data_path + 'mbe_data_' + date + '.xlsx') as writer:
        single_df.to_excel(writer, sheet_name='epic_log_data')

    return print('file successfully exported')