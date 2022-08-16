# Float Zone experiment


list of files in folder:
* ## schema file (.schema.archive.yaml)
  
  a yaml file containing the structure of ELN that will host user's data. Sections, subsections and quantities are the elements that compose the hierarchical structure of data. An important part of each element are the **annotations**, with which we enable the available ELN features such as: 
    * editability of quantities
    * automatic plot of quantities ([https://nomad-lab.eu/plot](https://nomad-lab.eu/prod/v1/staging/gui/dev/plot))
    * inheritance from specific Nomad base classes
    * drag and drop features for file upload
    * more at [https://nomad-lab.eu/editquantity](https://nomad-lab.eu/prod/v1/staging/gui/dev/editquantity)

* ## data file (.data.archive.yaml)
  a yaml file mimicking the same structure of the schema file. It lacks the infrastructural lines such as the sections ad subsections labeling or the annotations, types and units of quantities. It is used to avoid manual filling of data into ELN when they are repeated among multiple experiments. It also points to data files, metadata files, log files etc. where the actual number are stored. 

* ## data set 
  
  **FZ.xlsx** 

* ## data revision subfolder