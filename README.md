# Area A: sample preparation data

## Keywords: 
### Electronic Lab Notebook (ELN) / Application definition / Schemes / Data structures  

- - - -

This is a collection of blueprint schemas that include several kinds of experiment. 

The schemes here implemented are compliant to the NOMAD data structure: the hierarchy is composed by Sections, Subsections and Quantities (data fields).

The users can follow the info in this repo to build their own schema for their experiment :thumbsup:.

Each folder contains four categories of files, the user can try to drag and drop them in the upload page in nomad ([https://nomad-lab.eu/](https://nomad-lab.eu/)), they will be automatically parsed to create an "Entry" containing your experiment:

* schema file: it defines the structure that will host your data.
  The schema file has **.schema.archive.yaml** extension.

* data file: based on the schema file, it contains the actual data or links to metadata files, logfiles, dataset from instrument that will be parsed into your experiment Entry. The data file has **.data.archive.yaml** extension.

* data set: depending on the outcomes of the experiment, the user will have one or more files where the monitored parameters and metadata are stored. The data set files have **.txt.**, **.dat**, **.csv** or **.xlsx** extension.

* data revision: each user should collect and organize their own data structure as a guideline before starting to implement a schema. These helper files are placed in a subfolder.

- - - -
## The Structured Use Cases:

category | experiment | folder name
-|-|-|
Crystal Growth | Float Zone| FZ_IKZ
Crystal Growth | Melt Czochralski | melt_czochralski
 ? | Oxide Powder Preparation | oxide_powder_preparation
Epitaxial Growth | Metalorganic vapour-phase epitaxy Strontium Lantanium Oxide (MOVPE-STO) | movpe_STO
Epitaxial Growth | another epitaxy experiment | epitaxy
Electric properties | Hall Measurements | hall
Database | Material_db from IKZ | material_db_IKZ
Transmission | Transmission measurements | transmission