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

from structlog.stdlib import (
    BoundLogger,
)
from nomad_material_processing import (
    ActivityStep,
    Furnace,
    SampleDeposition,
    Crystal,
    Crucible,
    Tube,
)
from nomad.metainfo import (
    Package,
    Section,
    SubSection,
    Quantity,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    ArchiveSection,
)

m_package = Package(name='Crystal Growth')


class CrystalGrowthStep(ActivityStep):
    '''
    Details will be added later.
    '''
    pass


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
        unit='meter_per_second',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter_per_minute'
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



class CrystalGrowth(SampleDeposition):
    '''
    Any synthesis method used to grow crystals.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0002224"],
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )
    steps = SubSection(
        description='''
        The steps of the crystal growth.
        ''',
        section_def=CrystalGrowthStep,
        repeats=True,
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `CrystalGrowth` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CrystalGrowth, self).normalize(archive, logger)


class CzochralskiProcess(CrystalGrowth):
    '''
    A method of producing large single crystals (of semiconductors or metals) by
    inserting a small seed crystal into a crucible filled with similar molten
    material, then slowly pulling the seed up from the melt while rotating it.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0002158"],
    )
    method = Quantity(
        type=str,
        default='Czochralski Process'
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `CzochralskiProcess` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CzochralskiProcess, self).normalize(archive, logger)


class BridgmanFurnaceSection(ArchiveSection):
    furnace = Quantity(
        type=Furnace,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )

class InitialSynthesisComponent(Ensemble):
    pass


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


m_package.__init_metainfo__()
