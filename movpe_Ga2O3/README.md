# MOVPE Ga2O3 experiment

which files are in this folder:
 ## schema file (.schema.archive.yaml)
  
  a yaml file containing the ELN schema that will be used to host user's data. 
  
  Sections, subsections and quantities are the elements that compose the hierarchical structure of data. 
  
  An important part of each element are the **annotations**, with which we enable the available ELN features such as: 
    * editability of quantities [https://nomad-lab.eu/editquantity](https://nomad-lab.eu/prod/v1/staging/gui/dev/editquantity)
    * automatic plot of quantities ([https://nomad-lab.eu/plot](https://nomad-lab.eu/prod/v1/staging/gui/dev/plot))
    * inheritance from specific Nomad base classes (UserEditQuantity, AuthorEditQuantity)
    * drag and drop features for file upload (RawFileAdaptor)
    * more (overview: True, repeats: True, hide: ['..', '..'], template)

 ## data file (.data.archive.yaml)

  a yaml file built with the corresponding schema file structure. It lacks the "infrastructural" lines such as the sections and subsections labels or the annotations, types and units of quantities. It is used to avoid manual filling of data into ELN when they are repeated among multiple experiments. It also points to data files, metadata files, log files etc. where the actual number are stored. 

 ## data set 

 files are in preparation

 ## base classes subfolder

 this folder is placed in the root level of the repo, the user have to zip it and drag and drop together to the other files. The user finds a zipped copy of base_classes in each experiment folder.

---------
  #### drag and drop these file, together to "schema" and "data" files into the nomad upload page
