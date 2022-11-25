############################################################
#
# Python script to modify the original Excel log files from 
# IKZ before uploading them to NOMAD:
# - create Datum_Zeit as one datetime data column
# - add timezone information since NOMAD assumes UTC otherwise
# - save "Datum_Zeit" as String since Excel is not supporting 
#   timezone information
# - rename "Zonenhö" into "Zonenho"
#
#############################################################

import pandas as pd
from datetime import datetime

csvfile="G1_IKZ_NSI_23.csv"
df_csv=pd.read_csv(csvfile, sep=';', decimal=",")

df_csv['T Ist H1 Time'] = pd.to_datetime(df_csv['T Ist H1 Time'])
df_csv['T Ist H1 Time']=df_csv['T Ist H1 Time'].dt.tz_localize(tz="cet")

for i in df_csv:
    if 'Time' in i and 'T Ist H1 Time' not in i:
        del df_csv[i]
for i in df_csv:
    if '/' in i:
        new_i = i.replace('/', ' ')
        df_csv[new_i] = df_csv[i]
        del df_csv[i]

df_csv.to_csv(csvfile.split(".csv")[0]+"_for_NOMAD.csv", sep=';', decimal=".")
