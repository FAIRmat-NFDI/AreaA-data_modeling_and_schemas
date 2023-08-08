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

from structlog.stdlib import (
    BoundLogger,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    MEnum,
    Datetime,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from .custom_crystal_growth import (
    Crystal,
    Furnace,
    CrystalGrowthTube,
    InitialSynthesisComponent,
    Crucible,
)
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)
from nomad.datamodel.metainfo.eln import (
    ElementalComposition,
)

m_package = Package(name='CPFS SCHEMES')

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


class CPFSCrystalGrowthTube(CrystalGrowthTube,EntryData):
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
        The normalizer for the `CPFSCrystalGrowthTube` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(CrystalGrowthTube, self).normalize(archive, logger)
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
        The normalizer for the `CPFSCrucible` class.

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
        The normalizer for the `CPFSCrystal` class.

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
        The normalizer for the `CPFSInitialSynthesisComponent` class.

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

class CPFSRodInformation(ArchiveSection):
    rod_preparation=Quantity(
        type=str,
        description="""
        Any pre-treatment of the rod.
        """,
        a_eln={
            "component": "StringEditQuantity",
        },
    )
    seed_rod_diameter=Quantity(
        type=float,
        description='''
        The diameter of the seed rod.
        ''',
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "millimeter"
        },
        unit="meter",
    )
    feed_rod_diameter=Quantity(
        type=float,
        description='''
        The diameter of the feed rod.
        ''',
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "millimeter"
        },
        unit="meter",
    )
    feed_rod_crystal_direction=Quantity(
        type=str,
        description="""
        Crystal direction of the feed rod.
        """,
        a_eln={
            "component": "StringEditQuantity",
        },
    )

m_package.__init_metainfo__()
