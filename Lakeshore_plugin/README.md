# Lakeshore Plugin

This directory contains plugins designed for the IKZ institute.

See also:

[full IKZ_plugin README](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin)

[movpe_IKZ README](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin/src/movpe_IKZ)

## Structure

The directory tree:

```bash
Lakeshore_plugin/
├── nomad.yaml
├── src
│   └── hall
│       ├── nomad_plugin.yaml
│       ├── schema.py
│       ├── hall_instrument.py
│       ├── measurement.py
│       ├── reader.py
│       ├── nexus_to_msection.py
│       ├── helpers.py
│       ├── utils.py
│       ├── enum_map.json
│       ├── instrument_parser
│       │   ├── nomad_plugin.yaml
│       │   └── parser.py
│       └── measurement_parser
│           ├── nomad_plugin.yaml
│           └── parser.py
└── tests
    ├── data
    │   └── hall
    │       ├── 22-127-G_20K-320K_TT-Halter_WDH_060722.txt
    │       ├── 22-127-G_Hall-RT_TT-Halter.txt
    │       ├── 22-211-G_Hall_23K-320K_TT-Halter.txt
    │       ├── 23-026-AG_Hall_RT.txt
    │       ├── hall_eln_22-127-G_20K-320K_TT-Halter_WDH_060722.archive.yaml
    │       ├── hall_eln_22-127-G_Hall-RT_TT-Halter.archive.yaml
    │       ├── hall_eln_22-211-G_Hall_23K-320K_TT-Halter.archive.yaml
    │       ├── hall_eln_23-026-AG_Hall_RT.archive.yaml
    │       └── hall_eln.yaml
    └── test_parsing.py
```

- `src/`: contains the source code for the plugins.
- `tests/`: contains tests for the plugins.
- `hall/`: contains the source code for the hall measurement.
- `schema.py`, `hall_instrument.py`, `mesurement.py`: define the structure of the data after it has been parsed. It specifies the fields that the structured data will contain and the types of those fields.
- `parser.py` contains the logic for parsing the raw data from the MOVPE growth process. This includes reading the data from its original format, extracting the relevant information, and transforming it into a structured format.
- `reader.py`, `nexus_to_msection.py`, `helpers.py`, `utils.py`, `enum_map.json`: contain as well the logic for parsing the raw data from the MOVPE growth process. This includes reading the data from its original format, extracting the relevant information, and transforming it into a structured format.
- `nomad_plugin.yaml` defines the raw file matching rules of the parser. Check [NOMAD plugin official docs](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/plugins_dev.html#parser-plugin-metadata) for more info.

## Installation

To use these plugins, you need to:

* add the `src/` directory to your `PYTHONPATH`. You can do this by running the following command in the terminal where you run NOMAD:
```sh
export PYTHONPATH="$PYTHONPATH:/your/path/Lakeshore_plugin/src"
```
Export this system variable in the same terminal where you run NOMAD (`nomad admin run appworker`).

To make this path persistent, write into the .pyenv/bin/activate file of your virtual environment. Use the path of your local OS where you cloned this repository.

* include it in your `nomad.yaml` configuration file and specify the Python package for the plugin in the options section.
```yaml
plugins:
  include:
    - 'parsers/hall_lakeshore_measurement'
    - 'parsers/hall_lakeshore_instrument'
```
The name after the `/` is user defined.
Then, specify the Python package for the plugin in the options section:
```yaml
options:
    parsers/hall_lakeshore_measurement:
      python_package: hall.measurement_parser
    parsers/hall_lakeshore_instrument:
      python_package: hall.instrument_parser
```

This plugin does not require other plugins to be loaded. Althought, it is called in other plugins, you can clone them in your local machine:

```sh
git clone https://github.com/FAIRmat-NFDI/nomad-measurements
git clone https://github.com/FAIRmat-NFDI/nomad-material-processing
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas
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

## Usage

You need to copy and fill the tabular files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

> [!NOTE]
> The Lakeshore `.txt` files are missing metadata on the sample ID that is subject of the measurement, so the user need to navigate inside the measurement entry and reference manually the sample.

## Develop

### Fork the project

This project was forked from the github project page https://github.com/nomad-coe/nomad-schema-plugin-example

### Clone your fork

Follow the github instructions. The URL and directory depends on your user name or organization and the
project name you choose. But, it should look somewhat like this:

```
git clone git@github.com:markus1978/my-nomad-schema.git
cd my-nomad-schema
```

### Install the dependencies

You should create a virtual environment. You will need the `nomad-lab` package (and `pytest`).
You need at least Python 3.9.

```sh
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

to ensure installation of all the packages required, make sure in to install:

```sh
pip install nomad-lab[parsing, infrastructure]
```

### Run the tests

Make sure the current directory is in your path:

```sh
export PYTHONPATH=.
```

You can run automated tests with `pytest`:

```sh
pytest -svx tests
```

You can parse an example archive that uses the schema with `nomad` command
(installed via `nomad-lab` Python package):

```sh
nomad parse tests/data/test.archive.yaml --show-archive
```

### Developing your schema

Refer to official NOMAD docs to learn how to develop schemas and parsers and plugins, how to add them to an Oasis, how to publish them: https://nomad-lab/prod/v1/staging/docs/plugins.html
