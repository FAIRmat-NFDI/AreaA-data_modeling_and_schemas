# MOVPE IKZ Plugin

See also:

[full IKZ_plugin README](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin)

[LayTec README](https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin)

## Overview

This directory contains the MOVPE IKZ plugin for the NOMAD project.

The MOVPE IKZ plugin is used to parse and process data related to the MOVPE growth process at IKZ.

It is derived from the former yaml schema:[AreaA-data_modeling_and_schemas/movpe_IKZ_Ga2O3](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/movpe_IKZ_Ga2O3)

## Structure

The directory tree:

```bash
IKZ_plugin/
├── nomad.yaml
├── src
│   └── movpe_IKZ
│       ├── nomad_plugin.yaml
│       ├── schema.py
│       ├── movpe1_growth_parser
│       │   ├── constant_parameters
│       │   │   ├── nomad_plugin.yaml
│       │   │   └── parser.py
│       │   ├── deposition_control
│       │   │   ├── nomad_plugin.yaml
│       │   │   └── parser.py
│       │   └── parser.py
│       ├── movpe2_growth_parser
│       │   ├── nomad_plugin.yaml
│       │   └── parser.py
│       └── substrate_parser
│           ├── nomad_plugin.yaml
│           └── parser.py
└── tests
    └── data
        └── movpe_IKZ
            ├── movpe1_growth_parser
            │   ├── constant_parameters
            │   │   └── constant_parameters.xlsx  <--- template file
            │   └── deposition_control
            │       └── deposition_control.xlsx  <---- template file
            ├── movpe2_growth_parser
            │   └── GaO.growth.movpe.ikz.xlsx  <------ template file
            └── substrate_parser
                ├── GaO.substrates.movpe.ikz.xlsx  <-- template file
                └── Substrates-for-MOVPE1.xlsx
```

- `src/`: contains the source code of the plugin.
- `tests/`: contains the tests and template file to use with the plugin.
- `movpe1_growth_parser/`: contains the source code for machine "1" at IKZ.
- `movpe2_growth_parser/`: contains the source code for machine "2" at IKZ.
- `substrate_parser/`: contains the source code for substrate parser.
- `schema.py` defines the structure of the data after it has been parsed. It specifies the fields that the structured data will contain and the types of those fields.
- `parser.py` contains the logic for parsing the raw data from the MOVPE growth process. This includes reading the data from its original format, extracting the relevant information, and transforming it into a structured format.
- `nomad_plugin.yaml` defines the raw file matching rules of the parser. Check [NOMAD plugin official docs](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/plugins_dev.html#parser-plugin-metadata) for more info.

## Usage

* You need to copy and fill the excel files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

* Follow the raw file matching rules in `nomad_plugin.yaml` of each parser. In general, a file must:
  - have specific extension.
  - contain specific column headers.
> [!CAUTION]
> The parser is built to match specific template files. If files extension is changed or they are missing regex matching in the column headers, they might not be recognized by the parsers.

### `movpe1_growth_parser`

This folder contains two files with custom filename and `.xlsx` extension. Download these file if you use the "MOVPE 1" machine at IKZ.

* Upload the `constant_parameters.xlsx` file BEFORE the `deposition_control.xlsx` one to reference automatically the generated samples in each activity.

> [!NOTE]
> `deposition_control.xlsx` contains two sheets: "Deposition Control" and "Precursors". Each row is used to record one experiment.

* Fill the `Constant Parameters ID` with the same ID you write into the `constant_parameters.xlsx` file, in this way the parameters that remain constant across several experiments will be correctly referenced.
* Generate one row in "Deposition Control" sheet and in "Precursors" sheet for each growth experiment. They refer to the same sample and hence must contain the same unique `Sample ID`. An error will be thrown if the rows in the two sheets contain different `Sample ID` fields.

> [!NOTE]
> After uploading the `constant_parameters.xlsx` and `deposition_control.xlsx` files, please open `RawFileConstantParameters` and `RawFileDepositionControl` generated entries in NOMAD to check if there is some processing error. Carefully analize any warning or error and upload the file again if needed.

### `movpe2_growth_parser`

This folder contains one file with custom filename and `.growth.movpe.ikz.xlsx` extension. Download these file if you use the "MOVPE 2" machine at IKZ.

### `substrate_parser`

This folder contains one file with custom filename and `.substrates.movpe.ikz.xlsx` extension. Download these files to record info on Substrate used for both "MOVPE 1" and "MOVPE 2" machines at IKZ.



## Installation

To use these packages, you need to:

* add the `src/` directory to your `PYTHONPATH`. You can do this by running the following command in the terminal where you run NOMAD (`nomad admin run appworker`):
```sh
export PYTHONPATH="$PYTHONPATH:/your/path/IKZ_plugin/src"
```
Export this system variable in the same terminal where you run NOMAD (`nomad admin run appworker`).

To make this path persistent, write into the .pyenv/bin/activate file of your virtual environment. Use the path of your local OS where you cloned this repository.

* include it in your `nomad.yaml` configuration file and specify the Python package for the plugin in the options section.
```yaml
plugins:
  include:
    - 'parsers/movpe_growth_IKZ'
```
The name after the `/` is user defined.
Then, specify the Python package for the plugin in the options section:
```yaml
options:
  parsers/movpe_growth_IKZ:
    python_package: movpe_IKZ.binaryoxides_growth_parser
```

This plugin requires to clone in your local machines other plugin repositories:

```sh
git clone https://github.com/FAIRmat-NFDI/nomad-measurements
git clone https://github.com/FAIRmat-NFDI/nomad-material-processing
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas
( git clone https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin.git )
```

Consequentlty, other paths must be appended to `PYTHONPATH` system variable:

```sh
export MYPATH=/your/path
export PYTHONPATH=$PYTHONPATH:$MYPATH/PLUGINS/nomad-measurements/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/PLUGINS/nomad-measurements/src/nomad_measurements
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/hall/Lakeshore_plugin
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/IKZ_plugin/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/LayTec_EpiTT/laytec_epitt_plugin/src
( export PYTHONPATH=$PYTHONPATH:$MYPATH/laytec_epitt_nomad_plugin/src )
```

To load the full functionality, use the following `plugins` section:

```yaml
plugins:
  include:
    - 'schemas/nomad_measurements'
    - 'schemas/nomad_material_processing'
    - 'parsers/hall_lakeshore_measurement'
    - 'parsers/hall_lakeshore_instrument'
    - 'parsers/laytec_epitt'
    - 'schemas/basesections_IKZ'
    - 'parsers/cz_IKZ'
    - 'parsers/movpe_2_IKZ'
    - 'parsers/movpe_1_deposition_control_IKZ'
    - 'parsers/movpe_1_IKZ'
    - 'parsers/movpe_substrates_IKZ'
    - 'parsers/ds_IKZ'

  options:
    schemas/nomad_measurements:
      python_package: nomad_measurements
    schemas/nomad_material_processing:
      python_package: nomad_material_processing
    parsers/hall_lakeshore_measurement:
      python_package: hall.measurement_parser
    parsers/hall_lakeshore_instrument:
      python_package: hall.instrument_parser
    parsers/laytec_epitt:
      python_package: laytec_epitt
    schemas/basesections_IKZ:
      python_package: basesections_IKZ
    parsers/cz_IKZ:
      python_package: cz_IKZ
    parsers/movpe_2_IKZ:
      python_package: movpe_IKZ.movpe2_growth_parser
    parsers/movpe_1_deposition_control_IKZ:
      python_package: movpe_IKZ.movpe1_growth_parser.deposition_control
    parsers/movpe_1_IKZ:
      python_package: movpe_IKZ.movpe1_growth_parser.constant_parameters
    parsers/movpe_substrates_IKZ:
     python_package: movpe_IKZ.substrate_parser
    parsers/ds_IKZ:
      python_package: ds_IKZ
```
