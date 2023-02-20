# PVD process base classes
This directory contains the `schema.archive.yaml` files for defining the base classes of any Physical Vapor Deposition (PVD) process.

The directory contains the draft of the PVD base class as well as the deriving PVD
definitions for various labs and setups.

## Base class hierarchy
```
Activity
├── Process
.   ├── Synthesis
.   .   ├── VaporDeposition
.   .   .   ├── PVD
.   .   .   .   ├── EBeam
.   .   .   .   ├── MBE
    .   .   .   ├── Sputtering
        .   .   ├── Thermal
            .   └── PLD
            └── CVD
```
