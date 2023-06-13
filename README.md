# Area A: sample preparation data

## Keywords:  

### Electronic Lab Notebook (ELN) / Schemas / Data structures / NOMAD Uploads

## Base Sections Hierarchy:

![Base Sections](https://box.hu-berlin.de/f/b72febaaedb54162b74c/?dl=1)


The tree visualization shows the inheritance structure of our data model. 

This is a structure under development, for suggestions and contributes please refer to the issues opened in this repo.

See the NOMAD source code containing these classes at [this link](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-FAIR/-/blob/develop/nomad/datamodel/metainfo/basesections.py).
## About this repo:

It is a collection of example schemas that include several kinds of experiment.  

The schemas here implemented adapt to the NOMAD data structure: the hierarchy is composed by instances of Sections, Subsections and Quantities (data fields).

The users can follow the info in this repo to build their own schema for their experiment :thumbsup:.

Further explanations on NOMAD Metainfo and Archive [here](https://nomad-lab.eu/prod/v1/staging/docs/archive.html#custom-metainfo-schemas-eg-for-elns)

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

- - - -

In the subfolders, a dedicated README documents the file set for each use case.

- - - -
## The Structured Use Cases:

category | experiment | folder name
-|-|-|
Crystal Growth | Float Zone | float_zone_IKZ
Crystal Growth | Float Zone | float_zone_CPFS-Dresden
Crystal Growth | Flux growth | flux_growth_CPFS-Dresden
Crystal Growth | Melt Czochralski | melt_czochralski_Dadzis
Crystal Growth | Melt Czochralski | melt_czochralski_Dropka
Sinterization (Precursor Preparation) | Oxide Powder | oxide_powder_preparation
Epitaxial Growth | Metalorganic vapour-phase epitaxy Strontium Lantanium Oxide (MOVPE-SrTiO) | movpe_STO
Epitaxial Growth | Metalorganic vapour-phase epitaxy Gallium Oxide (MOVPE-Ga2O3) | movpe_Ga2O3
Epitaxial Growth | Metalorganic vapour-phase epitaxy (MOVPE) | movpe_CNR
Crystal Growth | Directional Solidification | directional_solidification_IKZ
Epitaxial Growth | Molecular Beam Epitaxy (MBE) | mbe_epitaxy
Epitaxial Growth | Molecular Beam Epitaxy (MBE) | mbe_SiGe
Sol-Gel Synthesis | Aerogels | aerogel_synthesis
Database | Material_db from IKZ | material_db_IKZ
Surface Coating | Spin-coating | surface_coating_methods
Surface Coating | Dip-coating | surface_coating_methods
Surface Coating | Sputtering | surface_coating_methods
Surface Coating | Evaporation | surface_coating_methods
Electric properties (Measurement) | Hall Measurements | hall
Transmission (Measurement) | Transmission measurements | transmission
AFM (Measurement) | Atomic Force Microscopy | AFM
Various | Experiments permormed in Max Planck Institute for Chemical Physics of Solids in Dresden | CPFS-Dresden

- - - -

