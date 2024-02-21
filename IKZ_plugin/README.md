# IKZ Plugin

This directory contains plugins designed for the IKZ institute.

See also:

[movpe README](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/IKZ_plugin/src/movpe)

## Structure

The directory tree:

```bash
IKZ_plugin/
├── nomad.yaml
├── src
│   ├── basesections
│   ├── czochralski
│   ├── directional_solidification
│   ├── mbe
│   └── movpe
└── tests
    └── data
        ├── basesections
        ├── czochralski
        ├── directional_solidification
        ├── mbe
        └── movpe
```

- `src/`: contains the source code for the plugins.
- `tests/`: contains tests for the plugins.

Please refer to the README.md file in each subdirectory for more information about each plugin.

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
    - 'parsers/movpe_2'
```
The name after the `/` is user defined.
Then, specify the Python package for the plugin in the options section:
```yaml
options:
  parsers/movpe_2:
    python_package: movpe.movpe2_growth_parser
```

This plugin requires to clone in your local machines other plugin repositories:

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
    - 'schemas/basesections'
    - 'parsers/czochralski'
    - 'parsers/movpe_2'
    - 'parsers/movpe_1_deposition_control'
    - 'parsers/movpe_1'
    - 'parsers/movpe_substrates'
    - 'parsers/directional_solidification'

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
    schemas/basesections:
      python_package: basesections
    parsers/czochralski:
      python_package: czochralski
    parsers/movpe_2:
      python_package: movpe.movpe2_growth_parser
    parsers/movpe_1_deposition_control:
      python_package: movpe.movpe1_growth_parser.deposition_control
    parsers/movpe_1:
      python_package: movpe.movpe1_growth_parser.constant_parameters
    parsers/movpe_substrates:
     python_package: movpe.substrate_parser
    parsers/directional_solidification:
      python_package: directional_solidification
```

## Usage

You need to copy and fill the tabular files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

Please refer to the README.md file in each subdirectory for more information about each plugin.

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
