# IKZ Plugin

This directory contains a plugin called `ikz_plugin` designed for the IKZ institute.

This a python package that contains several subpackages for each technique.

Check the README within each subfolder for more deatils on each technique.

## Structure

The directory tree:

```bash
IKZ_plugin/
├── src
│   └── ikz_plugin
│       ├── general
│       ├── characterization
│       ├── czochralski
│       ├── directional_solidification
│       ├── pld
│       ├── mbe
│       └── movpe
└── tests
    └── data
        ├── czochralski
        ├── directional_solidification
        ├── pld
        ├── mbe
        └── movpe
```

- `src/`: contains the source code for the plugins.
- `tests/`: contains tests for the plugins.

## Installation

To use the plugin, you need to clone this repo in your local machine and install the package with pip:

```bash
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas
cd IKZ_plugin
pip install -e .[dev]
```

For more details on what happens under the hood, check the `.toml` file in the `IKZ_plugin` folder:

- all the installed subpackages are listed under the section `[project.entry-points.'nomad.plugin']`.
- `dependencies` and `[project.optional-dependencies]` contain all the other packages installed along to this one.

## Usage

You need to copy and fill the tabular files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

Please refer to the README.md file in each subdirectory for more information about each plugin.

## Development

### Fork the project

This project was forked from the github project page <https://github.com/nomad-coe/nomad-schema-plugin-example>

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

### Install the plugin without pip

For some reason, you may want to avoid installation of the package with pip and plug this code to NOMAD in a more direct fashion:

- add the `src/` directory to your `PYTHONPATH`. You can do this by running the following command in the terminal where you run NOMAD:

```sh
export PYTHONPATH="$PYTHONPATH:/your/path/IKZ_plugin/src"
```

Export this system variable in the same terminal where you run NOMAD (`nomad admin run appworker`).

To make this path persistent, write into the .pyenv/bin/activate file of your virtual environment. Use the path of your local OS where you cloned this repository.

- include it in your `nomad.yaml` configuration file and specify the Python package for the plugin in the options section.

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
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/Lakeshore_plugin/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/LayTec_EpiTT_plugin/src
export PYTHONPATH=$PYTHONPATH:$MYPATH/AreaA-data_modeling_and_schemas/IKZ_plugin/src
```

To load the full functionality, use the following `plugins` section:

```yaml
plugins:
  include:
    - 'ikz_plugin.general:general_schema'
    - 'ikz_plugin.characterization:characterization_schema'
    - 'ikz_plugin.pld:pld_schema'
    - 'ikz_plugin.movpe:movpe_schema'
    - 'ikz_plugin.movpe.movpe2.growth_excel:movpe2_growth_excel_parser'
    - 'ikz_plugin.movpe.movpe1.growth_excel:movpe1_growth_excel_parser'
    - 'ikz_plugin.movpe.substrate:substrate_excel_parser'
    - 'ikz_plugin.mbe:mbe_schema'
    - 'ikz_plugin.directional_solidification:dir_sol_schema'
    - 'ikz_plugin.directional_solidification:dir_sol_manual_protocol_excel_parser'
    - 'ikz_plugin.czochralski:czochralski_schema'
    - 'ikz_plugin.czochralski:czochralski_multilog_parser'
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

Refer to official NOMAD docs to learn how to develop schemas and parsers and plugins, how to add them to an Oasis, how to publish them: <https://nomad-lab/prod/v1/staging/docs/plugins.html>
