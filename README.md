# Area A: materials synthesis and processing

## Keywords:

- Electronic Lab Notebook (ELN)
- Data Structures
- Custom YAML Schemas
- NOMAD Uploads

## About this repo:

It is a collection of example custom schemas shaped on the needs of different users.

The schemas here implemented adapt to the NOMAD data structure: the hierarchy is composed by instances of Sections, Subsections and Quantities (data fields).

The users can follow the info in this repo to build their own schema for their experiment 👍.

Further explanations on NOMAD are availbale in the [official documentation page](https://nomad-lab.eu/prod/v1/staging/docs/index.html)

Each folder contains several kind of files, the user can try to drag and drop all of them in the upload page in [Nomad](https://nomad-lab.eu/), they will be automatically parsed to create "Entries" containing the experimental data in a structured fashion:

* schema file: it is a NOMAD archive file (**.archive.yaml** extension) containing only one section called "definitions". It defines the structure that will host your data.

  Sections, subsections and quantities are the elements that compose the hierarchical structure of data.

  An important part in the schema is the **annotations** section, enabling the available ELN features such as:

  * [editability of quantities](https://nomad-lab.eu/prod/v1/staging/gui/dev/editquantity)
  * [automatic plot of quantities](https://nomad-lab.eu/prod/v1/staging/gui/dev/plot)
  * inheritance from specific Nomad base classes (ReferenceEditQuantity, AuthorEditQuantity)
  * drag and drop features for file upload (RawFileAdaptor)
  * more (overview: True, repeats: True, hide: ['..', '..'], template)
* data set: depending on the experiment, the user will have one or more files where the logged parameters and metadata are stored. The data set files have **.png**, **.tif**, **.txt.**, **.dat**, **.csv** or **.xlsx** extension.

## Base Sections Hierarchy:

The tree visualization shows the inheritance structure of our data model.
This structure is in continuous development and may quickly change from week to week.

For suggestions and contributes please refer to the issues opened in this repo.

See the NOMAD source code containing these classes at [this link](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-FAIR/-/blob/develop/nomad/datamodel/metainfo/basesections.py).

We are developing a more verbose documentation to describe the Base Section contained in each of the examples in this repo.

---

### In the subfolders, a dedicated README documents the file set for each use case.

The folders contain either YAML schemas or Plugins available for installation in your own NOMAD Oasis

---

## The Structured Use Cases:

| category                              | experiment                                                                              | folder name                    |
| ------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------ |
| Crystal Growth                        | Float Zone                                                                              | float_zone_IKZ                 |
| Crystal Growth                        | Float Zone                                                                              | float_zone_CPFS-Dresden        |
| Crystal Growth                        | Flux growth                                                                             | flux_growth_CPFS-Dresden       |
| Crystal Growth                        | Melt Czochralski                                                                        | melt_czochralski_Dadzis        |
| Crystal Growth                        | Melt Czochralski                                                                        | melt_czochralski_Dropka        |
| Sinterization (Precursor Preparation) | Oxide Powder                                                                            | oxide_powder_preparation       |
| Epitaxial Growth                      | Metalorganic vapour-phase epitaxy Strontium Lantanium Oxide (MOVPE-SrTiO)               | movpe_STO                      |
| Epitaxial Growth                      | Metalorganic vapour-phase epitaxy Gallium Oxide (MOVPE-Ga2O3)                           | movpe_Ga2O3                    |
| Epitaxial Growth                      | Metalorganic vapour-phase epitaxy (MOVPE)                                               | movpe_CNR                      |
| Crystal Growth                        | Directional Solidification                                                              | directional_solidification_IKZ |
| Epitaxial Growth                      | Molecular Beam Epitaxy (MBE)                                                            | mbe_epitaxy                    |
| Epitaxial Growth                      | Molecular Beam Epitaxy (MBE)                                                            | mbe_SiGe                       |
| Sol-Gel Synthesis                     | Aerogels                                                                                | aerogel_synthesis              |
| Database                              | Material_db from IKZ                                                                    | material_db_IKZ                |
| Surface Coating                       | Spin-coating                                                                            | surface_coating_methods        |
| Surface Coating                       | Dip-coating                                                                             | surface_coating_methods        |
| Surface Coating                       | Sputtering                                                                              | surface_coating_methods        |
| Surface Coating                       | Evaporation                                                                             | surface_coating_methods        |
| Electric properties (Measurement)     | Hall Measurements                                                                       | hall                           |
| Transmission (Measurement)            | Transmission measurements                                                               | transmission                   |
| AFM (Measurement)                     | Atomic Force Microscopy                                                                 | AFM                            |
| Various                               | Experiments permormed in Max Planck Institute for Chemical Physics of Solids in Dresden | CPFS-Dresden                   |

---

## Installation

To use the plugin packages maintained by FAIRmat Area A, you need to:

1. Clone this repo and, additionally, individual repos of other plugins like `nomad-measurement`.
2. Add their `src/` directory to your environmental variable `PYTHONPATH`.
3. Update the `nomad.yaml` file of present in the root of your local NOMAD installation.

### Cloning AreaA repos

You can run the following commands in your terminal to clone the GitHub repos containing AreaA plugins.

```sh
git clone https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas
git clone https://github.com/FAIRmat-NFDI/nomad-measurements
git clone https://github.com/FAIRmat-NFDI/nomad-material-processing
```

### Adding the package path to `PYTHONPATH`

To add the `src/` directory of the plugins to your `PYTHONPATH`, you can use the `export` command in your terminal. Make sure to do this in the same terminal before running NOMAD (`nomad admin run appworker`). Run the following command to include the actively maintained plugins:

```sh
export AREA_A_REPO_PATH="{local path to root of AreaA-data_modeling_and_schemas}"
export NOMAD_MEASUREMENTS_REPO_PATH="{local path to root of nomad-measurements}"
export NOMAD_MATERIAL_PROCESSING_REPO_PATH="{local path to root of nomad-material-processing}"
export PYTHONPATH="$PYTHONPATH:$AREA_A_REPO_PATH/IKZ_plugin/src"
export PYTHONPATH="$PYTHONPATH:$AREA_A_REPO_PATH/Lakeshore_plugin/src"
export PYTHONPATH="$PYTHONPATH:$AREA_A_REPO_PATH/LayTec_EpiTT/laytec_epitt_plugin/src"
export PYTHONPATH="$PYTHONPATH:$AREA_A_REPO_PATH/analysis_plugin/src"
export PYTHONPATH="$PYTHONPATH:$NOMAD_MEASUREMENTS_REPO_PATH/src"
export PYTHONPATH="$PYTHONPATH:$NOMAD_MEASUREMENTS_REPO_PATH/src/nomad_measurements"
export PYTHONPATH="$PYTHONPATH:$NOMAD_MATERIAL_PROCESSING_REPO_PATH/src/nomad_material_processing"
```

To make this path persistent, write these code lines into the `.pyenv/bin/activate` file of your virtual python environment. This automatically appends the paths every time the python environment is activated in a new terminal. Make sure to prepend the correct local path where you cloned this repository.

### Including the plugins in NOMAD config

To use the plugins in your NOMAD instance, include it in the `nomad.yaml` configuration file available in the root of your NOMAD installation. Additionally, you should also specify the Python package for the plugin in the `options` section as in the following snippet. Here there are listed all the currently available plugins in this repo and their dependences, pick the lines corresponding to the plugins you need:

```yaml
plugins:
  include:
    - 'parsers/hall_lakeshore_measurement'
    - 'parsers/hall_lakeshore_instrument'
    - 'schemas/basesections_IKZ'
    - 'parsers/cz_IKZ'
    - 'parsers/movpe_2_IKZ'
    - 'parsers/movpe_1_deposition_control_IKZ'
    - 'parsers/movpe_1_IKZ'
    - 'parsers/movpe_substrates_IKZ'
    - 'parsers/ds_IKZ'
    - 'schemas/nomad_material_processing'
    - 'parsers/laytec_epitt'
    - 'parsers/PPMS'
    - 'parsers/movpe_IMEM'
    - 'parsers/xrd'
    - 'schemas/nomad_measurements'
    - 'schemas/analysis'
  options:
    parsers/hall_lakeshore_measurement:
      python_package: hall.measurement_parser
    parsers/hall_lakeshore_instrument:
      python_package: hall.instrument_parser
    schemas/basesections_IKZ:
      python_package: basesections_IKZ
    parsers/cz_IKZ:
      python_package: cz_IKZ
    parsers/movpe_2_IKZ:
      python_package: movpe_IKZ.movpe2_growth_parser
    parsers/movpe_1_deposition_control_IKZ:
      python_package: movpe_IKZ.movpe1_growth_parser.deposition_control
    parsers/movpe_1_IKZ:
      python_package: movpe_IKZ.movpe1_growth_parser.constant_parameters
    parsers/movpe_substrates_IKZ:
     python_package: movpe_IKZ.substrate_parser
    parsers/ds_IKZ:
      python_package: ds_IKZ
    schemas/nomad_material_processing:
      python_package: nomad_material_processing
    parsers/laytec_epitt:
      python_package: laytec_epitt
    parsers/PPMS:
      python_package: PPMS
    parsers/movpe_IMEM:
      python_package: movpe_IMEM
    parsers/xrd:
      python_package: xrd
    schemas/nomad_measurements:
      python_package: nomad_measurements
    schemas/analysis:
      python_package: analysis
```

The name after the `/` in `include` section is user defined. However, same name should be used as key when specifying the python package in `options` section.

---
