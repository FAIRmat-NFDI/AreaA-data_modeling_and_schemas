# Area A: sample preparation data

## Keywords:  

### Electronic Lab Notebook (ELN) / Schemas / Data structures / NOMAD Uploads

- - - -
Full documentation (in preparation) at: https://fairmat-nfdi.github.io/AreaA-Documentation/
- - - -

## Base Classes Hierarchy:

![Base Classes](https://box.hu-berlin.de/f/d47b44f9f09543768f5b/?dl=1)


The tree visualization shows the inheritance structure contained in the base_classes file. 

This is a structure under development, for suggestions and contributes please refer to the issues opened in this repo.
## About this repo:

It is a collection of example schemas that include several kinds of experiment.  

The schemas here implemented adapt to the NOMAD data structure: the hierarchy is composed by Sections, Subsections and Quantities (data fields).

The users can follow the info in this repo to build their own schema for their experiment :thumbsup:.

Some further explanation on NOMAD Metainfo and Archive [here](https://nomad-lab.eu/prod/v1/staging/docs/archive.html#custom-metainfo-schemas-eg-for-elns)

Each folder contains four categories of files, the user can try to drag and drop all of them in the upload page in [Nomad](https://nomad-lab.eu/), they will be automatically parsed to create an "Entry" containing the experimental data in a structured fashion:

* schema file: it defines the structure that will host your data.
  The schema file has **.schema.archive.yaml** extension.

  Sections, subsections and quantities are the elements that compose the hierarchical structure of data. 

  An important part in the schema is the **annotations** section, enabling the available ELN features such as: 
    * [editability of quantities](https://nomad-lab.eu/prod/v1/staging/gui/dev/editquantity)
    * [automatic plot of quantities](https://nomad-lab.eu/prod/v1/staging/gui/dev/plot)
    * inheritance from specific Nomad base classes (ReferenceEditQuantity, AuthorEditQuantity)
    * drag and drop features for file upload (RawFileAdaptor)
    * more (overview: True, repeats: True, hide: ['..', '..'], template)

* data file: based on the schema file, it contains the actual data or links to metadata files, logfiles, dataset from instrument that will be parsed into your experiment Entry. The data file has **.data.archive.yaml** extension.

  It lacks the "infrastructural" lines such as the sections and subsections labels or the annotations, types and units of quantities, pesent in the schema file. It is used to avoid manual filling of data into ELN when they are repeated among multiple experiments. It also points to data files, metadata files, log files etc. where the actual number are stored. 

* data set: depending on the outcomes of the experiment, the user will have one or more files where the monitored parameters and metadata are stored. The data set files have **.txt.**, **.dat**, **.csv** or **.xlsx** extension.

* base classes: sections with fixed structure collected in base_classes folder, the user will find a copy of this base_classes file that must be included in the upload.

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

