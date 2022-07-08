# Data revision examples

Efficient data management requires consistent and well-structured and well-described data. Once the data is well organized the data can be imported with little effort in any data management systems or transformed into FAIR data. There are basic principles that can be applied on any data set to improve its consistency and its machine readability:

- each property in a data set requires an unique name,
- the information about the type of data (string, integer, float, date, etc.),
- a description of the property,
- the value of that property or the information where the values are stored,
- the unit of the value,
- information if this property is required or optional,
- and a specification in which group or section this property belongs.

In this folder we collect user examples of data revisions. A data revision can be carried out in any format, however, we recommend using a yaml text file. Yaml supports hierarchical data, is both machine and human readable. From a yaml-based data revision it is straight forward to develop a data schema which can be used in NOMAD, since NOMAD supports [custom schemas based on yaml files](https://nomad-lab.eu/prod/v1/staging/docs/archive.html#custom-metainfo-schemas-eg-for-elns).