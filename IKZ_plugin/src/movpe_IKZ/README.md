# MOVPE IKZ Plugin

This directory contains the MOVPE IKZ plugin for the NOMAD project.

## Overview

The MOVPE IKZ plugin is used to parse and process data related to the MOVPE growth process at IKZ.

## Structure

The directory structure is as follows:

- `movpe1_growth_parser/`: This directory contains the source code for machine "1" at IKZ.
- `movpe2_growth_parser/`: This directory contains the source code for machine "2" at IKZ.
- `substrate_parser/`: This directory contains the source code for substrate parser.

The `parser.py` file contains the logic for parsing the raw data from the MOVPE growth process. This includes reading the data from its original format, extracting the relevant information, and transforming it into a structured format.

The `schema.py` file defines the structure of the data after it has been parsed. It specifies the fields that the structured data will contain and the types of those fields.

## Installation

To use these plugins, you need to:

* add the `src/` directory to your `PYTHONPATH`. You can do this by running the following command in the terminal where you run NOMAD:
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
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/hall
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/LayTec_EpiTT
```

Consequentlty, other paths must be appended to `PYTHONPATH` system variable:

```sh
export MYPATH=/your/path
export PYTHONPATH=$PYTHONPATH:$MYPATH/PLUGINS/nomad-measurements/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/PLUGINS/nomad-measurements/src/nomad_measurements
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/hall/Lakeshore_plugin
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/LayTec_EpiTT/laytec_epitt_plugin/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/IKZ_plugin/src
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
      python_package: lakeshore.measurement_parser
    parsers/hall_lakeshore_instrument:
      python_package: lakeshore.instrument_parser
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

## Usage

You need to copy and fill the tabular files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

The available files are:

```
IKZ_plugin/tests/data/movpe_IKZ
├── movpe1_growth_parser
│   ├── constant_parameters
|   |   └── constant_parameters.xlsx
│   └── deposition_control
|       └── deposition_control.xlsx
├── movpe2_growth_parser
│   └── GaO.growth.movpe.ikz.xlsx
└── substrate_parser
    └── GaO.substrates.movpe.ikz.xlsx
```

`movpe1_growth_parser` contains two files with custom filename and `.xlsx` extension.

`movpe1_growth_parser` contains one file with custom filename and `.growth.movpe.ikz.xlsx` extension.

`substrate_parser` contains one file with custom filename and `.substrates.movpe.ikz.xlsx` extension.

!!! attention
    If the extension is not correct or the files miss some field,
    they might not be recognized by the parsers.
