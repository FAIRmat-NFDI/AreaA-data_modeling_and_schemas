# IKZ LayTec EpiTT Plugin

See also:

[full IKZ_plugin README](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin)
[movpe_IKZ README](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin/src/movpe_IKZ)


## Overview

This repo contains the LayTec EpiTT IKZ plugin for the NOMAD project.

The LayTec EpiTT IKZ plugin is used to parse and process data related to the LayTec EpiTT monitoring during metal-organic vapor phase epytaxy (MOVPE) process at IKZ.

## Structure

The directory structure is as follows:

```
laytec_epitt_nomad_plugin
├── nomad.yaml
├── src
│   └── laytec_epitt
│       ├── nomad_plugin.yaml
│       ├── parser.py
│       └── schema.py
└── tests
    ├── data
    │   └── <filename>.dat
    └── test_schema.py
```


- `src/`: This directory contains the source code of the plugin.
- `tests/`: This directory contains the tests and template file to use with the plugin.
- `parser.py` contains the logic for parsing the raw data. This includes reading the data from its original format, extracting the relevant information, and transforming it into a structured format.
- `schema.py` defines the structure of the data after it has been parsed. It specifies the fields that the structured data will contain and the types of those fields.
- `nomad_plugin.yaml` defines the raw file matching rules of the parser. Check [NOMAD plugin official docs](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/plugins_dev.html#parser-plugin-metadata) for more info.

## Usage

* You need to have a LayTec file as the one contained in `tests/data` folder, then drag and drop it into a new NOMAD upload.

* Follow the raw file matching rules in `src/nomad_plugin.yaml`. A file must:
  - have .dat extension.
  - contain the following string `FILETYPE = EpiNet DatArchiver File`. 
> [!CAUTION]
> The parser is built to match specific Laytec files. If files extension is changed or they are missing regex matching, they might not be recognized by the parsers.

* If the LayTec file contains a `RUN_ID` parameter that matches another existing entry for the growth process, the sample created during the growth process will be linked automatically in the LayTec mesurement entry, too. To create a growth process archive, install the IKZ_plugin and follow the [documentation of MOVPE_IKZ package](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin/src/movpe_IKZ).


## Installation

To use this package, you need to:

* add the `src/` directory to your `PYTHONPATH`. You can do this by running the following command in the terminal where you run NOMAD (`nomad admin run appworker`):

```bash
export PYTHONPATH="$PYTHONPATH:/your/path/laytec_epitt_nomad_plugin/src"
```

Export this system variable in the same terminal where you run NOMAD (`nomad admin run appworker`).

To make this path persistent, write into the .pyenv/bin/activate file of your virtual environment. Use the path of your local OS where you cloned this repository.

* include it in your `nomad.yaml` configuration file and specify the Python package for the plugin in the options section.
```yaml
plugins:
  include:
    - 'parsers/laytec_epitt'
```
The name after the `/` is user defined.
Then, specify the Python package for the plugin in the options section:
```yaml
options:
  parsers/laytec_epitt:
    python_package: laytec_epitt
```

This plugin requires to clone in your local machines other plugin repositories:

```sh
git clone https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin.git
git clone https://github.com/FAIRmat-NFDI/nomad-measurements
git clone https://github.com/FAIRmat-NFDI/nomad-material-processing
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas
```

Consequentlty, other paths must be appended to `PYTHONPATH` system variable:

```sh
export MYPATH=/your/path
export PYTHONPATH=$PYTHONPATH:$MYPATH/laytec_epitt_nomad_plugin/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/nomad-measurements/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/nomad-measurements/src/nomad_measurements
export PYTHONPATH=$PYTHONPATH:$MYPATH/nomad-material-processing/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/IKZ_plugin/src
```

To load the full functionality, use the following `plugins` section:

```yaml
plugins:
  include:
    - 'schemas/nomad_measurements'
    - 'schemas/nomad_material_processing'
    - 'parsers/laytec_epitt'
    - 'schemas/basesections_IKZ'
    - 'parsers/movpe_2_IKZ'
    - 'parsers/movpe_1_deposition_control_IKZ'
    - 'parsers/movpe_1_IKZ'
    - 'parsers/movpe_substrates_IKZ'

  options:
    schemas/nomad_measurements:
      python_package: nomad_measurements
    schemas/nomad_material_processing:
      python_package: nomad_material_processing
    parsers/laytec_epitt:
      python_package: laytec_epitt
    schemas/basesections_IKZ:
      python_package: basesections_IKZ
    parsers/movpe_2_IKZ:
      python_package: movpe_IKZ.movpe2_growth_parser
    parsers/movpe_1_deposition_control_IKZ:
      python_package: movpe_IKZ.movpe1_growth_parser.deposition_control
    parsers/movpe_1_IKZ:
      python_package: movpe_IKZ.movpe1_growth_parser.constant_parameters
    parsers/movpe_substrates_IKZ:
     python_package: movpe_IKZ.substrate_parser
```
