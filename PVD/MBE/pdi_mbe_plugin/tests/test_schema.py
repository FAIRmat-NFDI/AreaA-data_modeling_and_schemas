from parsermbepdi.normalizer import *

# date of the experiment
date = "2023_06_08"

# relative path
data_path = 'data/'

# resample to reduce the size of data arrays.
# '3T' for 3 minutes, '30S' for 30 seconds etc.
# Required only if resampling by time is needed.
resampling_period = '30S'

# pressure related log data will be filtered by the relative change
# that is given by a percentage.
percent_cut = 10
# temperature related log data will be filtered by the absolute change
# that is given by a value.
value_cut = 0.2

# if this boolean value is 1, then every log file will be written to
# a different sheet in *.xlsx file and will be kept as distinct
# DataFrames in the memory. If 0, then they are written as columns
# of a single sheet with same Date column. '0' method will only work
# with resampling by time.
write_method = 0

# Reading data files
dataframe_list = epiclog_read(date, data_path, percent_cut, value_cut, resampling_period)

# OPTIONAL: write to an *.xlsx file
if write_method == 1:
    epic_xlsx(date, data_path, dataframe_list)
else:
    single_df = epicdf_combine(dataframe_list)
    epic_xlsx_single(date, data_path, single_df)

