# Area A: materials synthesis and processing

## About this repo

It is a collection of example custom schemas shaped on the needs of different users.

The schemas here implemented adapt to the NOMAD data structure: the hierarchy is composed by instances of Sections, Subsections and Quantities (data fields).

The users can follow the info in this repo to build their own schema for their experiment 👍.

Further explanations on NOMAD are availbale in the [official documentation page](https://nomad-lab.eu/prod/v1/staging/docs/index.html)

Each folder contains several kind of files, the user can try to drag and drop all of them in the upload page in [Nomad](https://nomad-lab.eu/), they will be automatically parsed to create "Entries" containing the experimental data in a structured fashion:

* schema file: it is a NOMAD archive file (**.archive.yaml** extension) containing only one section called "definitions". It defines the structure that will host your data.
  Sections, subsections and quantities are the elements that compose the hierarchical structure of data.
* test datasets: depending on the experiment, the user will have one or more files where the logged parameters and metadata are stored. The data set files have **.png**, **.tif**, **.txt.**, **.dat**, **.csv** or **.xlsx** extension.

Some folders contain Python packages that are referred as PLUGINS.

**Check the README in each subdirectory for more info**.

## Basesections Hierarchy

The [tree visualizations](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/base_sections.html) represent the inheritance structure of our data model.
This structure is in continuous development and may quickly change from week to week.

For suggestions and contributes please refer to the issues opened in this repo.

See the NOMAD source code contains the [set of base sections](https://github.com/nomad-coe/nomad/blob/develop/nomad/datamodel/metainfo/basesections.py) developed so far.
Few more repo are used to collect general classes shared among different use cases: [nomad-measurements](https://github.com/FAIRmat-NFDI/nomad-measurements), [nomad-material-processing](https://github.com/FAIRmat-NFDI/nomad-material-processing).

We are developing a more verbose documentation to describe the basesections contained in each of the examples in this repo.

---

## Use Cases Summary

| Category            | Use Case                   | Institute | Code Type   | folder path                                                                                                                                                       |
| ------------------- | -------------------------- | --------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Crystal Growth      | Float Zone                 | IKZ       | YAML Schema | [float_zone_IKZ](AreaA-data_modeling_and_schemas/tree/124-move-pvd-techniques-in-ikz-plugin-folder/float_zone_IKZ)                                                   |
| Crystal Growth      | Float Zone                 |           |             | float_zone_CPFS-Dresden                                                                                                                                           |
| Crystal Growth      | Flux growth                |           |             | flux_growth_CPFS-Dresden                                                                                                                                          |
| Crystal Growth      | Melt Czochralski           | IKZ       | Plugin      | [czochralski](AreaA-data_modeling_and_schemas/tree/124-move-pvd-techniques-in-ikz-plugin-folder/IKZ_plugin/src/ikz_plugin/czochralski)                               |
| Crystal Growth      | Melt Czochralski           |           |             | melt_czochralski_Dropka                                                                                                                                           |
| Sinterization       | Oxide Powder               | IKZ       |             | oxide_powder_preparation                                                                                                                                          |
| Epitaxial Growth    | MOVPE-SrTiO                | IKZ       | Plugin      | [movpe_1](AreaA-data_modeling_and_schemas/tree/124-move-pvd-techniques-in-ikz-plugin-folder/IKZ_plugin/src/ikz_plugin/movpe/movpe1_growth_parser)                    |
| Epitaxial Growth    | MOVPE-Ga2O3                | IKZ       | Plugin      | [movpe_2](AreaA-data_modeling_and_schemas/tree/124-move-pvd-techniques-in-ikz-plugin-folder/IKZ_plugin/src/ikz_plugin/movpe/movpe2_growth_parser)                    |
| Epitaxial Growth    | MOVPE                      | IMEM-CNR  | Plugin      |  [movpe](https://github.com/IMEM-CNR-Parma/IMEM-NOMAD-plugins)                                                                                                                                                                |
| Crystal Growth      | Directional Solidification | IKZ       | Plugin      | [directional_solidification](AreaA-data_modeling_and_schemas/tree/124-move-pvd-techniques-in-ikz-plugin-folder/IKZ_plugin/src/ikz_plugin/directional_solidification) |
| Epitaxial Growth    | MBE                        | PDI       |             | mbe_epitaxy                                                                                                                                                       |
| Epitaxial Growth    | MBE                        | IKZ       |             | mbe_SiGe                                                                                                                                                          |
| Sol-Gel Synthesis   | Aerogels                   |           |             | aerogel_synthesis                                                                                                                                                 |
| Database            | Material_db from IKZ       | IKZ       |             | material_db_IKZ                                                                                                                                                   |
| Surface Coating     | Spin-coating               |           |             | surface_coating_methods                                                                                                                                           |
| Surface Coating     | Dip-coating                |           |             | surface_coating_methods                                                                                                                                           |
| Surface Coating     | Sputtering                 |           |             | surface_coating_methods                                                                                                                                           |
| Surface Coating     | Evaporation                |           |             | surface_coating_methods                                                                                                                                           |
| Electric properties | Hall Measurements          | IKZ       | Plugin      | [lakeshore_nomad_plugin](https://github.com/IKZ-Berlin/lakeshore-nomad-plugin)                                               |
| Optical properties | Reflectance          | IKZ       | Plugin      | [laytec_epitt_plugin](https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin)                                               |
| Transmission        | Transmission measurements  |           |             | transmission                                                                                                                                                      |
| AFM                 | Atomic Force Microscopy    |           |             | AFM                                                                                                                                                               |
| Various             |                            |           |             | CPFS-Dresden                                                                                                                                                      |

---

