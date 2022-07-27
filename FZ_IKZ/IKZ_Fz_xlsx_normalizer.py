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

xlsxfile="FZ_IKZ/nomad/1520___pro_(08.10.19).xlsx"
df_xlsx=pd.read_excel(xlsxfile, parse_dates=[["Datum","Zeit"]])
df_xlsx.Datum_Zeit=df_xlsx.Datum_Zeit.dt.tz_localize(tz="cet")
df_xlsx.Datum_Zeit=df_xlsx.Datum_Zeit.astype('str')
df_xlsx.Datum_Zeit=df_xlsx.Datum_Zeit.astype('str')
df_xlsx.rename(columns={"ZonenHö": "ZonenHo",}, inplace=True)
df_xlsx.to_excel(xlsxfile.split(".xlsx")[0]+"_for_NOMAD.xlsx")
