#

# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
from io import StringIO
import numpy as np
import pandas as pd
from datetime import datetime

from structlog.stdlib import (
    BoundLogger,
)
#from PPMS.schema import PPMSMeasurement, PPMSData, Sample, ChannelData, ETOData

from nomad.metainfo import Package, Section, MEnum, SubSection

from nomad.datamodel.metainfo.basesections import Measurement

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.data import (
    ArchiveSection,
)

from nomad.metainfo import (
    Package,
    Quantity,
)

from nomad.datamodel.metainfo.eln import (
    CompositeSystem,
)

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from nomad.datamodel.metainfo.basesections import ActivityStep

from cpfs_basesections.cpfs_schemes import (
    CPFSCrystal,
)

from nomad.search import search

from ppms.schema import (
    Sample,
    PPMSMeasurement,
)

from time import (
    sleep,
    perf_counter
)

m_package = Package(name='cpfs_ppms')


class CPFSSample(Sample):
    sample_id = Quantity(
        type=CPFSCrystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )

class CPFSPPMSMeasurement(PPMSMeasurement,EntryData):

    # m_def = Section(
    #     a_eln=dict(lane_width='600px'),
    #     a_plot={"plotly_graph_object": {
    #             "data": {
    #             "x": "#data/temperature",
    #             "y": "#data/field",
    #             },
    #         }
    # },
    # )
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                   'name',
                   'datetime',
                   'data_file',
                   'sequence_file',
                   'description',
                   'software',
                   'startupaxis',
               ],
            ),
            lane_width='600px',
            ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:

        super(CPFSPPMSMeasurement, self).normalize(archive, logger)

        with archive.m_context.raw_file(self.data_file, 'r') as file:
            data = file.read()

        header_match = re.search(r'\[Header\](.*?)\[Data\]', data, re.DOTALL)
        header_section = header_match.group(1).strip()
        header_lines = header_section.split('\n')

        sample1_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE1_' in line]
        if sample1_headers:
            sample_1 = CPFSSample()
            for line in sample1_headers:
                parts = re.split(r',\s*', line)
                key = parts[-1].lower().replace('sample1_','')
                if key=="sample_id":
                    search_result = search(
                        owner="user",
                        query={
                            "results.eln.sections:any": ["CPFSCrystal"],
                            "results.eln.names:any": [parts[1]+r'*']
                        },
                        user_id=archive.metadata.main_author.user_id,
                        )
                    if len(search_result.data)>0:
                        sample_1.sample_id=f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
                        sample_1.name=search_result.data[0]['search_quantities'][0]['str_value']
                    else:
                        logger.warning("The sample given in the header could not be found and couldn't be referenced.")
                elif hasattr(sample_1, key):
                    setattr(sample_1, key, ", ".join(parts[1:-1]))

        sample2_headers = [line for line in header_lines if line.startswith("INFO") and 'SAMPLE2_' in line]
        if sample2_headers:
            sample_2 = CPFSSample()
            for line in sample2_headers:
                parts = re.split(r',\s*', line)
                key = parts[-1].lower().replace('sample2_','')
                if key=="sample_id":
                    search_result = search(
                        owner="user",
                        query={
                            "results.eln.sections:any": ["CPFSCrystal"],
                            "results.eln.names:any": [parts[1]+r'*']
                        },
                        user_id=archive.metadata.main_author.user_id,
                        )
                    if len(search_result.data)>0:
                        sample_2.sample_id=f"../uploads/{search_result.data[0]['upload_id']}/archive/{search_result.data[0]['entry_id']}#data"
                        sample_2.name=search_result.data[0]['search_quantities'][0]['str_value']
                    else:
                        logger.warning("The sample given in the header could not be found and couldn't be referenced.")
                elif hasattr(sample_2, key):
                    setattr(sample_2, key, ", ".join(parts[1:-1]))

        while self.samples:
            self.m_remove_sub_section(CPFSPPMSMeasurement.samples, 0)
        self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample_1)
        self.m_add_sub_section(CPFSPPMSMeasurement.samples, sample_2)

m_package.__init_metainfo__()