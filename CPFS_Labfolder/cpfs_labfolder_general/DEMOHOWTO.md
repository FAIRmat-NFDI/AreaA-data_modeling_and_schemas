# Internal How-to:The Labfolder Import Plugin

This How-to describes the import of an entry from LabFolder to NOMAD via a mapping file. As an example, a CVT synthesis entry is used and the synthesized crystal is created as a separate archive in NOMAD.

Additionally, a PPMS measurement of that crystal can be parsed to show automatic recognition of that crystal archive and to demonstrate possible automatic analysis of the measurement.

## Prerequisites

- LabFolder entry of the CVT synthesis
- Mapping file
- NOMAD with the following plugins:
    - labfolder_general
    - cpfs_schemes
    - custom_crystal_growth
    - cpfs_cvt
    - PPMSMeasurement and CPFSPPMSMeasurement plugin
- PPMS measurement file (sequence file optional)

## Importing from LabFolder

In this part, the import from LabFolder in NOMAD is discussed. The respective LabFolder entry can be found with the following information

| | |
|---|---|
| link | https://labfolder.labforward.app/eln/notebook#?projectIds=280436 |
| entry id | 17340877 |
| login | nokyjona@physik.hu-berlin.de |
| password | LabfolderDemo24! |

The entry id is important for the next step, as LabFolder allows multiple (unrelated) entries per project and the import needs to pick the right one.

**Important note:** While the structure of the entry is the one really used at the CPfS, the content is only for demonstration and contains no valid scietific data.

To import in NOMAD, just create a new upload, choose 'Create from schema', and select the 'General Labfolder Project Import'. In the following page, enter all necessary information as given above together with the mapping file. After saving, new archive files (CPFSChemicalVapourTransport and CPFSCrystal) are created within the upload folder.

The CPFSChemicalVapourTransport contains all relevant data and a reference to the CPFSCrystal archive.

## Evaluating a PPMS measurement

To show the second part with the PPMS measurement analysis, just create a new upload and drop both data and sequence files in the upload. The following parsing takes a while (around 2 minutes on my oasis). In the data section of the created CPFSPPMSMeasurement archive the steps from the sequence file can be seen together with both symmetrized and analyzed data. In the plots section, the plots 'TMR', 'MR', 'Hall' (symmetrized data) and 'AHR', 'AHC', 'OHR' (analyzed data) are best for showing. They show all respective measurements in one plot and different temperatures can be selected or deselected.

In the files section, all symmetrized and analyzed data is stored in a file for each temperature together with one file 'analyzed_data_carrier_mobility_and_concentration_[...]', which contains the carrier concentration and mobility.