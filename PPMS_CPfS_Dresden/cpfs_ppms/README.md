# The CPfSPPMSMeasurement plugin

This plugin is an extension of the PPMSMeasurement plugin. All information from that plugin is also valid here. Additional functions implemented will be described in the following.

**Important note:** Most of the additional features are for now oly available for the ETO measurement mode of the PPMS.

## Additional functionalities

All functions of the PPMSMeasurement plugin are executed first. After that, the following additional steps are performed.

### Link the sample to an existing CPFSCrystal archive

The parser takes the sample id from the header line 'INFO, [...], SAMPLE[N]\_COMMENT' ([N] = 1 or 2) of the PPMS data file. The sample íd is expected to be in the first string of the comment between the first and second underscore (Python: line.split("_")[1]). The sample id must not contain underscores. The archive to link to needs to be of type CPFSCrystal and its name needs to start with the sample id. If no sample is found, the parser continues.

### Calculate resistivities from sample dimensions

The parser takes the sample dimensions from the header line 'INFO, [...], SAMPLE[N]\_MATERIAL' ([N] = 1 or 2) of the PPMS data file. The parser expects a comma separated list as [...] where the parts for length, width, and depth start with 'L=', 'w=', and 't='. All values are expected in 'mm'. If no dimensions are found, they are set to 1, leading to wrong quantities in the resistivities.

### Recognize measurement modes on the channels

The parser takes the sample id from the header line 'INFO, [...], SAMPLE[N]\_COMMENT' ([N] = 1 or 2) of the PPMS data file. In this line, it looks for the string 'Ch[N]_[mode]' with [N]= 1 or 2 and [mode] = Hall or TMR to identify, which channel performed which measurement. If this information is not found, the parser can not procced because the next steps need to distinguish between the two modes.

### Symmetrize the data

In the next step, all field-sweep measurements are symmetrized in field. If the measurements contain up- and downsweeps of the field (e.g. -9T -> 9T -> -9T), the full symmetrization is performed, if only up- or downsweep are present, the measurement is duplicated to simulate both sweeps. From the TMR the magnetoresistance MR is calculated. The symmetrized data is scaled with the sample dimensions to get resistivities and the separate measurements are plotted and stored to files starting with 'symmetrized_data_'.

### Analyze the data

The last step calculates the longitudinal conductivity, the ordinary Hall resistivity and the anomalous Hall resistivity and conductivity. Additionally, for each temperature the carrier concentration and mobility is calculated. The analyzed data is plotted and stored to files starting with 'analyzed_data_'.