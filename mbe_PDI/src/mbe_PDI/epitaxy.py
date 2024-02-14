import numpy as np
import re
from datetime import datetime as dt
import pandas as pd
import json

from nomad.datamodel.metainfo.basesections import (
    ElementalComposition,
    Activity,
    PureSubstance,
    ProcessStep,
    CompositeSystem,
    Measurement,
    MeasurementResult,
    Process,
    Collection,
    EntityReference,
    CompositeSystemReference,
    SectionReference,
    Experiment
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.files import StagingUploadFiles
from nomad.metainfo.metainfo import (
    MProxy,
    QuantityReference
)
from nomad.parsing.tabular import (
    TableData,
    create_archive
)
from structlog.stdlib import (
    BoundLogger,
)
from nomad.metainfo import (
    MSection,
    Package,
    Quantity,
    SubSection,
    MEnum,
    Reference,
    Datetime,
    Section,
    QuantityReference
)
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
    Author
)

from nomad.datamodel.datamodel import (
    EntryArchive,
    EntryMetadata
)

from nomad.utils import hash

#from laytec_epitt import LayTec_EpiTT_Measurement
#from lakeshore import HallMeasurement

from mbe_PDI import MbePDIExperiment

m_package = Package(name='mbe_PDI_epitaxy')

class MolecularBeamEpitaxy(Epitaxy):
    '''
    A synthesis method which consists of depositing a monocrystalline film (from a
    molecular beam) on a monocrystalline substrate under high vacuum (<10^{-8} Pa).
    Molecular beam epitaxy is very slow, with a deposition rate of <1000 nm per hour.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]

    Synonyms:
     - MBE
     - molecular-beam epitaxy
    '''
    m_def = Section(
        links=[
            "http://purl.obolibrary.org/obo/CHMO_0001341"
        ],)

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `MolecularBeamEpitaxy` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(MolecularBeamEpitaxy, self).normalize(archive, logger)