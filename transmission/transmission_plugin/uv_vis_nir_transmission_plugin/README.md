# UV-Vis Transmission Plugin

## Getting started

### Install your python plugin package

You should create a virtual environment.
You need at least Python 3.9.
From the top directory of your plugin you can install it en editable mode with:

```sh
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install -e .[dev] --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality, make
sure to include NOMAD's internal package registry (e.g. via `--index-url`).

### Run the tests

You can run automated tests with `pytest`:

```sh
pytest -svx tests
```

You can parse an example archive that uses the schema with `nomad`
(installed via `nomad-lab` Python package):

```sh
nomad parse tests/data/test.archive.yaml --show-archive
```
