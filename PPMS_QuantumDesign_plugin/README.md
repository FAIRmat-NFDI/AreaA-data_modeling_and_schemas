# NOMAD's Lakeshore plugin

## Getting started

### Fork the project

This plugin for originally forked from the github project page https://github.com/nomad-coe/nomad-schema-plugin-example
For more docs on how to build a plugin, follow the link.
Hit fork (and leave a star, thanks!). Maybe you want to rename the project while forking!

### Clone your fork

Follow the github instructions. The URL and directory depends on your user name or organization and the project name you choose. But, it should look somewhat like this:

```sh
git clone git@github.com:markus1978/my-nomad-schema.git
cd my-nomad-schema
```

### Install the dependencies

You should create a virtual environment. You will need the `nomad-lab` package (and `pytest`).
You need at least Python 3.9.

```sh
virtualenv --python=python3.9 .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt
```

### Run the tests

Make sure the current directory is in your path, you need to export it every time you open a new terminal:

```sh
export PYTHONPATH="$PYTHONPATH:/your/path/to/AreaA-data_modeling_and_schemas/hall/Lakeshore_plugin/Lakeshore"
```

or, even better, to make this path persistent write within the .pyenv/bin/activate file of your virtual environment the full path where you cloned this repo.

You can run automated tests with `pytest`:

```sh
pytest -svx tests
```

You can parse an example archive that uses the schema with `nomad`
(the command installed via `nomad-lab` Python package):

```sh
nomad parse tests/data/hall_eln_23-026-AG_Hall_RT.archive.yaml --show-archive
```

## Developing your schema

You can now start to develop you schema. Here are a few things that you might want to change:

- The metadata in `nomad_plugin.yaml`.
- The name of the Python package `nomadschemaexample`. If you want to define multiple plugins, you can nest packages.
- The name of the example section `ExampleSection`. You will also want to define more than one section.
- When you change module and class names, make sure to update the `nomad_plugin.yaml` accordingly.


## Build the python package

The `pyproject.toml` file contains everything that is necessary to turn the project
into a pip installable python package. Run the python build tool to create a package distribution:

```
pip install build
python -m build --sdist
```

You can install the package with pip:

```
pip install dist/nomad-schema-plugin-example-1.0.tar.gz
```

Read more about python packages, `pyproject.toml`, and how to upload packages to PyPI
on the [PyPI documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/).


## Next steps

To learn more about plugins, how to add them to an Oasis, how to publish them, read our
documentation on plugins: https://nomad-lab.eu/docs/plugins/plugins.html.

## To plug this plugin into your Oasis

the nomad.yaml in the root folder of your local installation should have the same lines found in the nomad.yaml in this folder:

```yaml
normalize:
  normalizers:
    include:
      - MetainfoNormalizer
plugins:
  include:
    - 'schemas/hall_IKZ'
  options:
    schemas/hall_IKZ:
      python_package: hall_IKZ

```

as before, do not forget to export the package path in the same terminal where you run NOMAD (`nomad admin run appworker`):

```python
export PYTHONPATH="$PYTHONPATH:/your/path/to/AreaA-data_modeling_and_schemas/hall/Lakeshore_plugin/Lakeshore"
```
