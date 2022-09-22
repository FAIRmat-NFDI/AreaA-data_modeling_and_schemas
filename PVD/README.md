# PVD process base classes
This directory contains the `schema.archive.yaml` files for defining the base classes of any Physical Vapor Deposition (PVD) process.

## Base class hierarchy
```
Activity
├── Process
.   ├── Synthesis
.   .   ├── PVD
.   .   .   ├── EBeam
    .   .   ├── Sputtering
        .   ├── Thermal
            └── PLD
```