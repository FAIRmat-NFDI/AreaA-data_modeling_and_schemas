# Area A: sample preparation data

## Keywords: 
### Electronic Lab Notebook (ELN) / Application definition / Schemes / Data structures  

- - - -

This is a collection of blueprint schemes that include several kinds of experiment. 

The schemes here implemented are compliant to the NOMAD data structure: the hierarchy is composed by Sections, Subsections and Quantities (data fields).

The users can follow the info in this repo to build their own schema for their experiment :thumbsup:.

Each folder contains four categories of files, the user can try to drag and drop the first three categories in the upload page in nomad ([https://nomad-lab.eu/](https://nomad-lab.eu/)), they will be automatically parsed to create an "Entry" containing the experimental data in a structured fashion:

* schema file: it defines the structure that will host your data.
  The schema file has **.schema.archive.yaml** extension.

* data file: based on the schema file, it contains the actual data or links to metadata files, logfiles, dataset from instrument that will be parsed into your experiment Entry. The data file has **.data.archive.yaml** extension.

* data set: depending on the outcomes of the experiment, the user will have one or more files where the monitored parameters and metadata are stored. The data set files have **.txt.**, **.dat**, **.csv** or **.xlsx** extension.

* data revision: each user should collect and organize their own data structure as a guideline before starting to implement a schema. These helper files are placed in a subfolder.

- - - -

In the subfolders a dedicated README documents the file set present for each use case.

- - - -
## The Structured Use Cases:

category | experiment | folder name
-|-|-|
Crystal Growth | Float Zone| FZ_IKZ
Crystal Growth | Melt Czochralski | melt_czochralski_Dadzis
Crystal Growth | Melt Czochralski | melt_czochralski_Dropka
 ? | Oxide Powder Preparation | oxide_powder_preparation
Epitaxial Growth | Metalorganic vapour-phase epitaxy Strontium Lantanium Oxide (MOVPE-SrTiO) | movpe_STO
Epitaxial Growth | Metalorganic vapour-phase epitaxy Gallium Oxide (MOVPE-Ga2O3) | movpe_Ga2O3
Epitaxial Growth | another epitaxy experiment | epitaxy
Macromolecular Self-assembly | Water-Air Interface Self-assembly | wai_synthesis
Electric properties | Hall Measurements | hall
Database | Material_db from IKZ | material_db_IKZ
Spin coating | Spin coating | spin_coating_aachen
Transmission | Transmission measurements | transmission
Various | Experiments permormed in Max Planck Institute for Chemical Physics of Solids in Dresden | CPFS-Dresden

- - - -

## A Schema Prototype

#### Main Sections

* User
* Instrument
* Materials
* Process