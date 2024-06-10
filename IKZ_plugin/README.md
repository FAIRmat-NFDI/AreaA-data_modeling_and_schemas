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

Refer to official NOMAD docs to learn how to develop schemas and parsers and plugins, how to add them to an Oasis, how to publish them: <https://nomad-lab/prod/v1/staging/docs/plugins.html>
