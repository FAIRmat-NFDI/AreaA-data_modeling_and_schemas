from parsermbepdi.normalizer import *

# date of the experiment
date = "2023_06_08"

# relative path
data_path = 'data/'

# resample to reduce the size of data arrays.
# '3T' for 3 minutes, '30S' for 30 seconds etc.
resampling_period = '3T'

dataframe_list = epiclog_read(date, data_path, resampling_period)
single_df = epicdf_combine(dataframe_list)
epic_xlsx(date, data_path, single_df)