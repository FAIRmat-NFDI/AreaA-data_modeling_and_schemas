# NOMAD's metinfo-yaml2py plugin

## Getting started

### Install your python plugin package

You should create a virtual environment.
You need at least Python 3.9.
From the top directory of your plugin you can install it en editable mode with:

```sh
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install -e . --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality. Make
sure to include NOMAD's internal package registry (e.g. via `--index-url`). Follow the instructions
in `requirements.txt`.

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

## Developing your schema

You can now start to develop you schema. Here are a few things that you might want to change:

- The metadata in `nomad_plugin.yaml`.
- The name of the Python package `nomadschemaexample`. If you want to define multiple plugins, you can nest packages.
- The name of the example section `ExampleSection`. You will also want to define more than one section.
- When you change module and class names, make sure to update the `nomad_plugin.yaml` accordingly.

To learn more about plugins, how to add them to an Oasis, how to publish them, read our
documentation on plugins: https://nomad-lab/prod/v1/staging/docs/plugins.html
