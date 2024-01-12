# Analyis Plugin

## Analyses parsed data files

This plugin is used to analyze parsed data files. It creates a Jupyter notebook
and links the data files to it. The notebook can be used to analyze the data.

## Setup for deployment on NOMAD Oasis (or plugin development)
Read the [NOMAD plugin documentation](https://nomad-lab.eu/prod/v1/staging/docs/plugins/plugins.html#add-a-plugin-to-your-nomad) for all details on how to deploy the plugin on your NOMAD instance.

Steps:
1. Clone the repo

    ```git clone git@github.com:FAIRmat-NFDI/AreaA-data_modeling_and_schemas.git```
2. Add the path of the plugin package inside the cloned repo to the `PYTHONPATH`

    ```export PYTHONPATH=$PYTHONPATH:{REPOSITORY PATH}/AreaA-data_modeling_and_schemas/analysis_plugin/src```
3. Modify the ```nomad.yaml``` configuration file of your NOMAD instance.

    ```yaml
    plugins:
    include:
        - 'schemas/analysis'
    options:
        schemas/analysis:
        python_package: analysis
    ```
