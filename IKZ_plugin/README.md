# NOMAD's schema example plugin

## Getting started

your nomad.yaml in your local installation should have this:

```yaml
keycloak:
  realm_name: fairdi_nomad_test
north:
  hub_connect_ip: '172.17.0.1'
normalize:
  normalizers:
    include:
      - MetainfoNormalizer
plugins:
  include:
    - 'schemas/basesections_IKZ'
    - 'schemas/hall_IKZ'
    - 'schemas/mbe_IKZ'
    - 'schemas/ds_ikz'
  options:
    schemas/basesections_IKZ:
      python_package: basesections_IKZ
    schemas/hall_IKZ:
      python_package: hall_IKZ
    schemas/mbe_IKZ:
      python_package: mbe_IKZ
    schemas/ds_IKZ:
      python_package: ds_IKZ
```

do not forget to export the package in the same terminal where you run NOMAD (`nomad admin run appworker`):

```python
export PYTHONPATH="$PYTHONPATH:/your/path/nomad-to/nomad-schema-plugin-x-ray-diffraction"
```

or to make this path persistent, write into the .pyenv/bin/activate file of your virtual env. Use the path of your local OS where you cloned this repo.

### Fork the project

Go to the github project page https://github.com/nomad-coe/nomad-schema-plugin-example, hit
fork (and leave a star, thanks!). Maybe you want to rename the project while forking!

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

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality. Make
sure to include NOMAD's internal package registry (e.g. via `--index-url`). Follow the instructions
in `requirements.txt`.

### Run the tests

Make sure the current directory is in your path:

```sh
export PYTHONPATH=.
```

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
