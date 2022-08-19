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

In the subfolders, a dedicated README documents the file set for each use case.

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

These section haven't got an a priori inheritance and the user can decide whether to place some of them inside others. As an example: a process can describe a sample history (synthesis and preparation) or also an instrument history (substitued components or consumables)

* **User**

* **Instrument**

* **Materials**

  a list of all the ID-labeled samples used or produced during experiment. This list should include:
  
  *  reagents for synthesis steps
  *  products of synthesis steps
  *  gas or liquid carriers that may be employed in a deposition
  *  substrates where a deposition happens
  *  even more kind of samples that the user may want to keep track of

* **Process**
  
  a list of steps describing the key actions performed during sample preparation. 
  
  More generally, an history of what happened to the sample, or to the instrument, ecc

  Several categories were envisioned:

  *  pre-process (annealing, polishing, ...)
  *  process (synthesis, sintering, evaporation, ...)
  *  post-process (annealing, cutting, ...)
  *  measurement (characterization after or during sample preparation)
  *  storage
  *  even more action shall be included here