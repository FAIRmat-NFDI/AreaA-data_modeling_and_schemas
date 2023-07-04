# MBE process base classes
This directory will contain the `mbe_pdi.NEW.schema.archive.yaml` files for defining the base classes of any Molecular Beam Epitaxy (MBE) process.

The directory contains the draft of the MBE schema as well as the deriving MBE
definitions for MBE Labs in Paul-Drude-Institut (PDI)

## Base class hierarchy
```
Activity
├── Process
.   ├── Synthesis
.   .   ├── VaporDeposition
.   .   .   ├── PVD
.   .   .   .   ├── EBeam
.   .   .   .   ├── **MBE**
    .   .   .   ├── Sputtering
        .   .   ├── Thermal
            .   └── PLD
            └── CVD
```

* Initial datamodel for the schema can be found in datamodel.md file.
* related log files need to be parsed to a *.csv/*.xlsx file.