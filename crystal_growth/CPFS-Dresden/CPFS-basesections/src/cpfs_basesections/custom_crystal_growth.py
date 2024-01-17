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

from nomad_material_processing.crystal_growth import (
    CrystalGrowth,
    CrystalGrowthStep,
)
from structlog.stdlib import (
    BoundLogger,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad.datamodel.data import (
    ArchiveSection,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.eln import (
    SampleID,
    Ensemble,
    Instrument,
)

m_package = Package(name='CUSTOM CRYSTAL GROWTH')


class Crystal(Ensemble):

    sample_id = Quantity(
        type=str,
        description='''
        Sample ID given by the grower.
        ''',
        a_eln={
            "component": "StringEditQuantity",
        },
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
    material=Quantity(
        type=str,
        description='''
        The material the furnace is made of.
        '''
    )
    geometry=Quantity(
        type=str,
        description='''
        The geometry of the furnace.
        '''
    )
    heating=Quantity(
        type=str,
        description='''
        The heating type of the furnace.
        '''
    )
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `Furnace` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Instrument, self).normalize(archive, logger)

class InitialSynthesisComponent(Ensemble):
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `InitialSynthesisComponent` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Ensemble, self).normalize(archive, logger)


class Crucible(ArchiveSection):
    material=Quantity(
        type=str,
        description='''
        The material of the crucible.
        ''',
        a_eln={
            "component": "StringEditQuantity",
        },
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

class CrystalGrowthTube(ArchiveSection):
    material=Quantity(
        type=str,
        description='''
        The material of the tube.
        ''',
        a_eln={
            "component": "StringEditQuantity",
        },
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
        a_eln={
            "component": "StringEditQuantity",
        },
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
    furnace = SubSection(
        section_def=Furnace,
    )
    crucible = SubSection(
        section_def=Crucible,
    )
    tube = SubSection(
        section_def=CrystalGrowthTube,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        description='''
        The step of the Bridgman Technique.
        ''',
        section_def=BridgmanTechniqueStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
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


class ChemicalVapourTransportStep(CrystalGrowthStep):
    '''
    A step in the Chemical Vapour Transport. Contains 2 temperatures and transport agent.
    '''
    temperature_one = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius'
        ),
    )
    temperature_two = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius'
        ),
    )
    transport_agent = SubSection(
        section_def=Ensemble,
    )


class ChemicalVapourTransport(CrystalGrowth):
    '''
    A crystal growth method for metal dichalcogenides in which the starting materials
    (high purity metal and chalcogen) are placed in a quartz ampoule together with a
    transport agent (e.g. iodine) and heated in a furnace under a temperature gradient.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0002652"],
    )
    method = Quantity(
        type=str,
        default='Chemical Vapour Transport',
    )
    furnace = SubSection(
        section_def=Furnace,
    )
    tube = SubSection(
        section_def=CrystalGrowthTube,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        description='''
        The step of the ChemicalVapourTransport.
        ''',
        section_def=ChemicalVapourTransportStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ChemicalVapourTransport` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ChemicalVapourTransport, self).normalize(archive, logger)


class CzochralskiProcessStep(CrystalGrowthStep):
    '''
    A step in the Czochralski Process.
    '''
    melting_power_in_percent = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    growth_power_in_percent = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    rotation_speed = Quantity(
        type=float,
        unit='hertz',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='hertz'
        ),
    )
    rotation_direction = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
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


class CzochralskiProcess(CrystalGrowth):
    '''
    A method of producing large single crystals (of semiconductors or metals) by
    inserting a small seed crystal into a crucible filled with similar molten material,
    then slowly pulling the seed up from the melt while rotating it.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0002158"],
    )
    method = Quantity(
        type=str,
        default='Czochralski Process',
    )
    furnace = SubSection(
        section_def=Furnace,
    )
    crucible = SubSection(
        section_def=Crucible,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        description='''
        The step of the Czochralski Process.
        ''',
        section_def=CzochralskiProcessStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
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


class ChemicalVapourTransportStep(CrystalGrowthStep):
    '''
    A step in the Chemical Vapour Transport. Contains 2 temperatures and transport agent.
    '''
    temperature_one = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius'
        ),
    )
    temperature_two = Quantity(
        type=float,
        unit='kelvin',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius'
        ),
    )
    transport_agent = SubSection(
        section_def=Ensemble,
    )
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ChemicalVapourTransportStep` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ChemicalVapourTransportStep, self).normalize(archive, logger)


class ChemicalVapourTransport(CrystalGrowth):
    '''
    A crystal growth method for metal dichalcogenides in which the starting materials
    (high purity metal and chalcogen) are placed in a quartz ampoule together with a
    transport agent (e.g. iodine) and heated in a furnace under a temperature gradient.
    [database_cross_reference: https://orcid.org/0000-0002-0640-0422]
    '''
    m_def = Section(
        links=["http://purl.obolibrary.org/obo/CHMO_0002652"],
    )
    method = Quantity(
        type=str,
        default='Chemical Vapour Transport',
    )
    furnace = SubSection(
        section_def=Furnace,
    )
    tube = SubSection(
        section_def=CrystalGrowthTube,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        description='''
        The step of the ChemicalVapourTransport.
        ''',
        section_def=ChemicalVapourTransportStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `ChemicalVapourTransport` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(ChemicalVapourTransport, self).normalize(archive, logger)


class FloatingZoneProcessStep(CrystalGrowthStep):
    '''
    A step in the Floating Zone Process, for now same as CzochralskiProcessStep.
    '''
    melting_power_in_percent = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    growth_power_in_percent = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    rotation_speed = Quantity(
        type=float,
        unit='hertz',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='hertz'
        ),
    )
    rotation_direction = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
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


class FloatingZoneProcess(CrystalGrowth):
    '''
    To be added, is not in CHMO
    '''
    m_def = Section(
        links=[""],
    )
    method = Quantity(
        type=str,
        default='Floating Zone Process',
    )
    furnace = SubSection(
        section_def=Furnace,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        description='''
        The step of the Floating Zone Process.
        ''',
        section_def=FloatingZoneProcessStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `FloatingZoneProcess` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(FloatingZoneProcess, self).normalize(archive, logger)

class FluxGrowthProcessStep(CrystalGrowthStep):
    '''
    A step in the Flux Growth Process.
    '''
    process_time = Quantity(
        type=float,
        unit='second',
        shape=['*'],
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='hour',
        )
    )
    temperature = Quantity(
        type=float,
        unit='kelvin',
        shape=['*'],
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        )
    )


class FluxGrowthProcess(CrystalGrowth):
    '''
    To be added, is not in CHMO
    '''
    m_def = Section(
        links=[""],
    )
    method = Quantity(
        type=str,
        default='Flux Growth Process',
    )
    furnace = SubSection(
        section_def=Furnace,
    )
    crucible = SubSection(
        section_def=Crucible,
    )
    tube = SubSection(
        section_def=CrystalGrowthTube,
    )
    initial_materials = SubSection(
        section_def=InitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        description='''
        The step of the FluxGrowthProcesss.
        ''',
        section_def=FluxGrowthProcessStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=Crystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `FluxGrowthProcess` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(FluxGrowthProcess, self).normalize(archive, logger)

m_package.__init_metainfo__()



