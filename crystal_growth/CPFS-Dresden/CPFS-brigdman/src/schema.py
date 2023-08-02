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
    MEnum,
    Datetime,
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
    ElementalComposition,
)

m_package = Package(name='MPI CPFS BRIDGMAN')


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
        The normalizer for the `BridgmanTechnique` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Instrument, self).normalize(archive, logger)

class InitialSynthesisComponent(Ensemble):
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechnique` class.

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

class BridgmanTube(ArchiveSection):
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
        section_def=BridgmanTube,
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




class CPFSFurnace(Furnace,EntryData):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'model',
                    'material',
                    'geometry',
                    'heating',
                ],
            ),
            lane_width='600px',
        ),
    )
    name = Quantity(
        type=MEnum(
            'Furnace1',
            'Furnace2',
            'Furnace3',
        ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
    )
    lab_id = Quantity(
        type=str,
        description='''An ID string that is unique at least for the lab that produced this
            data.''',
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
    )
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `CPFSFurnace` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Furnace, self).normalize(archive, logger)
        if self.name:
            furnace_list=[
                ["Furnace1","FurnaceModel1","Steel","Box","Induction"],
                ["Furnace2","FurnaceModel2","Cast Iron","Cube","Resistance"],
                ["Furnace3","FurnaceModel3","Titanium","",""],
            ]
            for li in furnace_list:
                if self.name==li[0]:
                    self.model=li[1]
                    self.material=li[2]
                    self.geometry=li[3]
                    self.heating=li[4]
                    break


class CPFSBridgmanTube(BridgmanTube,EntryData):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'material',
                    'diameter',
                    'filling',
                ],
            ),
            lane_width='600px',
        ),
    )
    name = Quantity(
        type=MEnum(
            'TubeType1',
            'TubeType2',
            'TubeType3',
        ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
    )
    lab_id = Quantity(
        type=str,
        description='''An ID string that is unique at least for the lab that produced this
            data.''',
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
    )
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechnique` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(BridgmanTube, self).normalize(archive, logger)
        if self.name:
            furnace_list=[
                ["TubeType1","Quartz","0.011","Vacuum"],
                ["TubeType2","Tantalum","0.012","Iodine"],
                ["TubeType3","Quartz","0.010",""],
            ]
            for li in furnace_list:
                if self.name==li[0]:
                    self.material=li[1]
                    self.diameter=float(li[2])
                    self.filling=li[3]
                    break


class CPFSCrucible(Crucible,EntryData):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'material',
                    'diameter',
                ],
            ),
            lane_width='600px',
        ),
    )
    name = Quantity(
        type=MEnum(
            'CrucibleType1',
            'CrucibleType2',
            'CrucibleType3',
        ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
    )
    lab_id = Quantity(
        type=str,
        description='''An ID string that is unique at least for the lab that produced this
            data.''',
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
    )
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechnique` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Crucible, self).normalize(archive, logger)
        if self.name:
            furnace_list=[
                ["CrucibleType1","Al","0.011"],
                ["CrucibleType2","Tantalum","0.012"],
                ["CrucibleType3","Al","0.010"],
            ]
            for li in furnace_list:
                if self.name==li[0]:
                    self.material=li[1]
                    self.diameter=float(li[2])
                    break



class CPFSCrystal(Crystal,EntryData):
    achieved_composition = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        )
    )
    final_crystal_length = Quantity(
        type=float,
        unit='meter',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
    )
    single_poly = Quantity(
        type=MEnum(
            'Single crystal',
            'Polycrystal',
        ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    crystal_shape = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        )
    )
    crystal_orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        )
    )
    safety_reactivity = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        )
    )
    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
    )
    lab_id = Quantity(
        type=str,
        description='''An ID string that is unique at least for the lab that produced this
            data.''',
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='StringEditQuantity', label='Remarks'),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechnique` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(Crystal, self).normalize(archive, logger)


class CPFSInitialSynthesisComponent(InitialSynthesisComponent,EntryData):
    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
    )
    lab_id = Quantity(
        type=str,
        description='''An ID string that is unique at least for the lab that produced this
            data.''',
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
    )
    state = Quantity(
        type=MEnum(
            'Powder',
            'Polycrystal',
            'Plate',
        ),
        a_eln=ELNAnnotation(
            component='EnumEditQuantity',
        ),
    )
    weight = Quantity(
        type=float,
        unit='gram',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram'
        ),
    )
    providing_company = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
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
        super(InitialSynthesisComponent, self).normalize(archive, logger)
        '''Figure out elemental composition from name if possible'''
        all_elements = [
                         'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
                         'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V',
                         'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As',
                         'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc',
                         'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',
                         'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu',
                         'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
                         'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po',
                         'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am',
                         'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg',
                         'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts',
                         'Og'
            ]
        if self.name:
            elements=[]
            nums=[]
            tmp_atom=self.name[0]
            tmp_number=""
            for i in range(1,len(self.name)):
                if self.name[i].isalpha():
                    if self.name[i].isupper():
                        elements.append(tmp_atom)
                        if tmp_number=="": tmp_number="1"
                        nums.append(int(tmp_number))
                        tmp_atom=self.name[i]
                        tmp_number=""
                    if self.name[i].islower():
                        tmp_atom+=self.name[i]
                if self.name[i] in "1234567890":
                    tmp_number+=self.name[i]
            elements.append(tmp_atom)
            if tmp_number=="": tmp_number="1"
            nums.append(int(tmp_number))

            elemental_comp=[]
            for i in range(len(nums)):
                elemental=ElementalComposition(
                    element=elements[i],
                    atomic_fraction=float(nums[i])/sum(nums)
                )
                elemental_comp.append(elemental)
            self.elemental_composition=elemental_comp




class CPFSBridgmanTechniqueStep(BridgmanTechniqueStep,EntryData):
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechnique` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(BridgmanTechniqueStep, self).normalize(archive, logger)










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
                ],
            ),
            lane_width='600px',
        ),
    )
    furnace = SubSection(
        section_def=CPFSFurnace,
    )
    crucible = SubSection(
        section_def=CPFSCrucible,
    )
    tube = SubSection(
        section_def=CPFSBridgmanTube,
    )
    initial_materials = SubSection(
        section_def=CPFSInitialSynthesisComponent,
        repeats=True,
    )
    steps = SubSection(
        section_def=CPFSBridgmanTechniqueStep,
        repeats=True,
    )
    resulting_crystal = Quantity(
        type=CPFSCrystal,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )
    xlsx_file = Quantity(
        type=str,
        description='''
        The xlsx file with data (optional). (.xlsx file).
        ''',
        a_browser=BrowserAnnotation(
            adaptor='RawFileAdaptor'
        ),
        a_eln=ELNAnnotation(
            component='FileEditQuantity'
        ),
    )
    lab_id = Quantity(
        type=str,
        description='''An ID string that is unique at least for the lab that produced this
            data.''',
    )
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
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
        self.location="MPI CPfS Dresden"
        if self.xlsx_file:
            import pandas as pd
            with archive.m_context.raw_file(self.xlsx_file, 'r') as xlsx:
                inp=pd.read_csv(xlsx)
                if inp.loc[2][1].split()[1]=="CPFSBridgmanTechnique":
                    self.name=str(inp.loc[10][2])
                    self.furnace = CPFSFurnace(name=str(inp.loc[13][2]))
                    self.furnace.normalize(archive,logger)
                    self.crucible = CPFSCrucible(name=str(inp.loc[14][2]))
                    self.crucible.normalize(archive,logger)
                    self.tube = CPFSBridgmanTube(name=str(inp.loc[15][2]))
                    self.tube.normalize(archive,logger)
                    step=[]
                    step.append(CPFSBridgmanTechniqueStep(
                        temperature=float(inp.loc[27][2])+273.15,
                        pulling_rate = float(inp.loc[28][2])/1000/60,
                                                        ))
                    self.steps = step
                    components=[]
                    for i in range(5):
                        if not pd.isna(inp.loc[20+i][1]):
                            single_component = CPFSInitialSynthesisComponent(
                                name=str(inp.loc[20+i][1]),
                                state=str(inp.loc[20+i][2]),
                                weight=float(inp.loc[20+i][3]),
                                providing_company=str(inp.loc[20+i][4]),
                            )
                            single_component.normalize(archive,logger)
                            components.append(single_component
                            )
                    self.initial_materials = components
                    crystal_ref = create_archive(
                        CPFSCrystal(
                            name = str(inp.loc[31][2]) + "_" + str(inp.loc[32][2]),
                            sample_id = str(inp.loc[31][2]),
                            achieved_composition = str(inp.loc[32][2]),
                            final_crystal_length = float(inp.loc[33][2])/1000,
                            single_poly = str(inp.loc[34][2]),
                            crystal_shape = str(inp.loc[35][2]),
                            crystal_orientation = str(inp.loc[36][2]),
                            safety_reactivity = str(inp.loc[37][2]),
                            description = str(inp.loc[38][2]),
                        ),
                        archive,
                        str(inp.loc[31][2]) + "_" + str(inp.loc[32][2]) + "_CPFSCrystal.archive.json"
                    )
                    self.resulting_crystal = crystal_ref
                else:
                    self.xlsx_file="Not a valid CPFSBridgmanTechnique template."

m_package.__init_metainfo__()
