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

from nomad_material_processing.utils import (
    create_archive,
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
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    BrowserAnnotation,
    SectionProperties,
)
from cpfs_basesections.custom_crystal_growth import (
    BridgmanTechnique,
    BridgmanTechniqueStep,
)
from cpfs_basesections.cpfs_schemes import (
    CPFSFurnace,
    CPFSCrystal,
    CPFSCrucible,
    CPFSCrystalGrowthTube,
    CPFSInitialSynthesisComponent,
)

m_package = Package(name='MPI CPFS BRIDGMAN')

class CPFSBridgmanTechniqueStep(BridgmanTechniqueStep,EntryData):
    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `BridgmanTechniqueStep` class.

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
        section_def=CPFSCrystalGrowthTube,
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
        The normalizer for the `Bridgman Technique` class.

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
                    self.tube = CPFSCrystalGrowthTube(name=str(inp.loc[15][2]))
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
