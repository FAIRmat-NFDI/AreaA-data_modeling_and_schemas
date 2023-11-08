# NOMAD's schema example plugin

## Getting started

The `nomad.yaml` file in your local installation should have these lines added:

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
    - 'schemas/MovpeIMEM'
    - 'parsers/MovpeIMEM'
  options:
    schemas/MovpeIMEM:
      python_package: movpe_IMEM
    parsers/MovpeIMEM:
      python_package: movpe_IMEM
```

Export the path of the package in the `PYTHONPATH` system variable inside the same terminal where you run NOMAD `nomad admin run appworker` (to make it persistent, add it to your .pyenv/bin/activate file):

```python
export PYTHONPATH="$PYTHONPATH:/your/path/AreaA-data_modeling_and_schemas/IMEM-CNR_plugin/src"
```

In the path there is `AreaA-data_modeling_and_schemas` because the best practice would be to clone this full repo in local as it may contain several plugins correlated. Note that the python package included in the `nomad.yaml` is inside the `src` folder.

The first plugin being included in the `nomad.yaml` file is contained in the following repo, it is called inside the IMEM plugin, so it must be loaded as well:
https://github.com/FAIRmat-NFDI/nomad-material-processing
The plugin in the following repo is also becoming important and will be at some point called inside the IMEM-CNR one:
https://github.com/FAIRmat-NFDI/nomad-measurements


To run this plugin as a standalone tool without NOMAD, follow [this tutorial](https://www.youtube.com/watch?v=_5hADA1QVw8&list=PLrRaxjvn6FDW-_DzZ4OShfMPcTtnFoynT&index=1&ab_channel=FAIRmatandNOMAD)

It is a tutorial to get started with plugin implementation, and it also shows how to run it as standalone tool, test it, etc.
The example used there can be found here: https://github.com/nomad-coe/nomad-schema-plugin-example

To learn more about plugins, how to add them to an Oasis, how to publish them, read our
documentation on plugins: https://nomad-lab/prod/v1/staging/docs/plugins.html

For any further question, consult the forum: https://matsci.org/c/nomad/32
or contact directly the team mantaining this plugin: andrea.albino@physik.hu-berlin.de hampus.naesstroem@physik.hu-berlin.de sebastian.brueckner@physik.hu-berlin.de