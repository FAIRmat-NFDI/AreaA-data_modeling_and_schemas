# Sample ID Workshop 

08.06.2022 9:00h - 12:00h, Zoom

Host: Sebastian Brückner (coordinator Area A)

## Participants:

Sebastian Brückner, Markus Kühbach, Hampus Näsström, Martin Albrecht, Johannes Lehmeyer, Pepe Marquez Prieto, Tamás Haraszti, Luca Ghiringhelli, Kerstin Helbig, Heiko Weber, Sherjeel Shabih, Fabian Zemke, Oliver Bierwagen, Sandor Brockhauser, Andrea Albino, Thomas Unold, Florian Dobener, Jonathan Noky, Carola Emminger

## Agenda:
1. Introduction 
2. User examples
    - suggestions on practical requirements
    - unique ID vs. meaningful/human readable name 
    - sample provenance and inheritance
3. What is needed within FAIRmat/NOMAD?

## Conclusion:

-	Need for pid / uid
    -	given by NOMAD for each upload and each entry within Upload
    -	for any sample (also unpublished ones)
    -	(Relation between pids needed --> sample inheritance)
    -	Not replacing sample ID (see below)
-	Need for individual sample ID 
    -	human readable --> internal use, understand sample without using computer
    -	Examples seen in the workshop contained information about:
        -	Sample owner
        -	Date stamp (or acronym)
        -	Sample name (individual lab defined)
        -	Institute (in an individual case)
    -	**we can provide a suggested solution**, that people can decide to adopt or not.
    -	**should be in NOMAD metainfo**
    -	Consider sample aliases
-	Implementation:
    -	Pepe creates a md-file in our github:  https://github.com/FAIRmat-Experimental/Area_A_application_definitions/blob/main/sampleid_workshop/sampleid.md
-	md-file: A convention for generation of a human readable sample id, as the basis for a “sample_id base class“ that serves as a suggestion to users who need a sample id system/workflow
-	Anyone can comment on it in github
-	When we reach an agreement it will be included in NOMAD 





