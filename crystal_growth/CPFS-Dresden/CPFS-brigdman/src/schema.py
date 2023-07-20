#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import re
import datetime

from typing import Union
from nomad_material_processing import (
    ActivityStep,
)
from nomad_material_processing.crystal_growth import (
    CrystalGrowth,
    CrystalGrowthStep,
)
from nomad_material_processing.utils import (
    create_archive,
)
from structlog.stdlib import (
    BoundLogger,
)
from nomad.units import (
    ureg,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    BrowserAnnotation,
    SectionProperties,
)
from nomad.datamodel.metainfo.eln import (
    SampleID,
    Substance,
    Component,
    Ensemble,
    Instrument,
)

m_package = Package(name='MPI CPFS BRIDGMAN')


class Crystal(Ensemble):

    sample_id = Quantity(
        type=str,
        description='''
        Sample ID given by the grower.
        ''',
    )

    internal_sample_id = SubSection(
        section_def=SampleID,
    )


class Furnace(Instrument):
    model=Quantity(
        type=str,
        description='''
        The model type of the furnace.
        ''',
    )

class InitialSynthesisComponent(Ensemble):
    pass

class Crucible(ArchiveSection):
    material=Quantity(
        type=str,
        description='''
        The material of the crucible.
        ''',
    )
    diameter=Quantity(
        type=float,
        description='''
        The diameter of the crucible.
        ''',
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "millimeter"
        },
        unit="meter",
    )

class Tube(ArchiveSection):
    material=Quantity(
        type=str,
        description='''
        The material of the tube.
        ''',
    )
    diameter=Quantity(
        type=float,
        description='''
        The diameter of the tube.
        ''',
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "millimeter"
        },
        unit="meter",
    )
    filling=Quantity(
        type=str,
        description='''
        The filling of the tube.
        ''',
    )



class BridgmanTechniqueStep(CrystalGrowthStep):
    '''
    A step in the Bridgman technique. Contains temperature and pulling rate.
    '''
    temperature = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius'
        ),
    )
    pulling_rate = Quantity(
        type=float,
        unit='meter/second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter/minute'
        ),
    )
    furnace = SubSection(
        section_def=Furnace,
    )
    crucible = SubSection(
        section_def=Crucible,
    )
    tube = SubSection(
        section_def=Tube,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )


class BridgmanTechnique(CrystalGrowth):
    '''
    A method of growing a single crystal 'ingot' or 'boule'. The polycrystalline sample is
    heated in a container above its melting point and slowly cooled from one end where a
    seed crystal is located. Single crystal material is then progressively formed along
    the length of the container.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0002160"],
    )
    method = Quantity(
        type=str,
        default='Bridgman Technique',
    )
    steps = SubSection(
        description='''
        The step of the Bridgman Technique.
        ''',
        section_def=BridgmanTechniqueStep,
        repeats=True,
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechnique` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(BridgmanTechnique, self).normalize(archive, logger)


class CPFSBridgmanTechnique(BridgmanTechnique, EntryData):
    '''
    Application definition section for a Bridgman technique at MPI CPFS.
    '''
    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0002160'],
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'end_time',
                    'lab_id',
                    'steps',
                ],
            ),
            lane_width='800px',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `CrystalGrowth` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(BridgmanTechnique, self).normalize(archive, logger)

m_package.__init_metainfo__()
