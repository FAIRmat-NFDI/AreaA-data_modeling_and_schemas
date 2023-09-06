import numpy as np
import re
from datetime import datetime as dt
import pandas as pd
import json

from nomad.units import ureg
from nomad.metainfo import (
    Package, Quantity, SubSection, MEnum, Reference, Datetime, Section)
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.eln import PublicationReference
from nomad.datamodel.metainfo.workflow import Link
from nomad.datamodel.metainfo.eln import Entity, Activity, SampleID
from nomad.datamodel.util import parse_path
from basesections_IKZ import SampleCut

m_package = Package(name='movpe_IKZ')



m_package.__init_metainfo__()
