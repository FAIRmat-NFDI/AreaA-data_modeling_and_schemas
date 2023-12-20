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

import nomad.datamodel as nodm

from nomad.datamodel.metainfo.eln.labfolder import LabfolderProject

from nomad.metainfo import Package, Section, MEnum, SubSection, Quantity

from nomad.datamodel.data import (
    EntryData,
)


from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)

from structlog.stdlib import (
    BoundLogger,
)

from nomad_material_processing.utils import (
    create_archive,
)

from cpfs_bridgman.bridgman import (
    CPFSBridgmanTechnique,
    CPFSBridgmanTechniqueStep
)

from cpfs_basesections.cpfs_schemes import (
    CPFSFurnace,
    CPFSCrystal,
    CPFSCrucible,
    CPFSCrystalGrowthTube,
    CPFSInitialSynthesisComponent,
)

m_package = Package(name='cpfs_labfolder')

class CPFSLabfolderProject(LabfolderProject,EntryData):

    import_entry_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:

        super(CPFSLabfolderProject, self).normalize(archive, logger)

        if self.import_entry_id:
            for entry in self.entries:
                logger.info(str(entry.id),str(self.import_entry_id))
                if str(entry.id)==str(self.import_entry_id):
                    #More general way possible?
                    #For now include Bridgman
                    import json
                    if "Bridgman" in entry.tags:
                        logger.info("Bridgman template found.")
                        for element in entry.elements:
                            if element.element_type=="DATA":
                                content=element.labfolder_data
                                if 'Monitored parameters' in content:
                                    step=[CPFSBridgmanTechniqueStep(
                                        temperature=float(content["Monitored parameters"]["Temperature"]["value"])+273.15,
                                        pulling_rate=float(content["Monitored parameters"]["Rate of pulling"]["value"])/60000.
                                    )]
                                    title="Basic features of the as-grown crystal"
                                    achieved_composition=content[title]["Achieved Composition"]["description"]
                                    final_length=float(content[title]["Final crystal length"]["value"])/1000.
                                    crystal_shape=content[title]["Crystal shape"]["description"]
                                    crystal_orientation=content[title]["Crystal orientation"]["description"]
                                    safety=content[title]["Safety/ Reactivity"]["description"]
                                if 'General info' in content:
                                    sample_id=content["General info"]["Sample ID"]["description"]
                                    furnace=CPFSFurnace(
                                        model=content["Setup and instruments"]["Furnace"]["Furnace name"]["description"]
                                    )
                                    crucible=CPFSCrucible(
                                        material=content["Setup and instruments"]["Crucible"]["Crucible material"]["description"],
                                        diameter=float(content["Setup and instruments"]["Crucible"]["Crucible diameter"]["value"])/1000.
                                    )
                                    tube=CPFSCrystalGrowthTube(
                                        material=content["Setup and instruments"]["Tube"]["Tube material"]["description"],
                                        diameter=float(content["Setup and instruments"]["Tube"]["Tube diameter"]["value"])/1000.,
                                        filling=content["Setup and instruments"]["Tube"]["Tube filling"]["description"]
                                    )
                            if element.element_type=="TABLE":
                                if element.title=="Initial elements/materials":
                                    materials=[]
                                    table=element.content["sheets"]["Sheet1"]["data"]["dataTable"]
                                    for i in range(1,len(table)):
                                        mat=CPFSInitialSynthesisComponent(
                                            name=table[str(i)]["0"]["value"],
                                            state=table[str(i)]["1"]["value"],
                                            weight=table[str(i)]["2"]["value"],
                                            providing_company=table[str(i)]["3"]["value"],
                                        )
                                        materials.append(mat)
                        crystal_ref=create_archive(
                            CPFSCrystal(
                                name = sample_id + "_" + achieved_composition,
                                sample_id = sample_id,
                                achieved_composition = achieved_composition,
                                final_crystal_length = final_length,
                                #single_poly = entry.elements[5].data_elements[1].children[2].description,
                                crystal_shape = crystal_shape,
                                crystal_orientation = crystal_orientation,
                                safety_reactivity = safety,
                                #description = str(inp.loc[38][2]),
                            ),
                            archive,
                            sample_id + "_" + achieved_composition + "_CPFSCrystal.archive.json"
                        )
                        create_archive(
                            CPFSBridgmanTechnique(
                                furnace=furnace,
                                crucible=crucible,
                                tube=tube,
                                steps=step,
                                initial_materials=materials,
                                resulting_crystal=crystal_ref,
                            ),
                            archive,
                            sample_id + "_" + achieved_composition + "_CPFSBridgmanTechnique.archive.json"
                        )









                        # materials=[]
                        # table=entry.elements[4].content["sheets"]["Sheet1"]["data"]["dataTable"]
                        # for i in range(1,len(table)):
                        #     mat=CPFSInitialSynthesisComponent(
                        #         name=table[str(i)]["0"]["value"],
                        #         state=table[str(i)]["1"]["value"],
                        #         weight=table[str(i)]["2"]["value"],
                        #         providing_company=table[str(i)]["3"]["value"],
                        #     )
                        #     materials.append(mat)
                        # crystal_ref=create_archive(
                        #     CPFSCrystal(
                        #         name = entry.elements[2].data_elements[0].children[0].description + "_" + entry.elements[5].data_elements[1].children[0].description,
                        #         sample_id = entry.elements[2].data_elements[0].children[0].description,
                        #         achieved_composition = entry.elements[5].data_elements[1].children[0].description,
                        #         final_crystal_length = entry.elements[5].data_elements[1].children[1].value/1000.,
                        #         #single_poly = entry.elements[5].data_elements[1].children[2].description,
                        #         crystal_shape = entry.elements[5].data_elements[1].children[3].description,
                        #         crystal_orientation = entry.elements[5].data_elements[1].children[4].description,
                        #         safety_reactivity = entry.elements[5].data_elements[1].children[5].description,
                        #         #description = str(inp.loc[38][2]),
                        #     ),
                        #     archive,
                        #     entry.elements[2].data_elements[0].children[0].description + "_" + entry.elements[5].data_elements[1].children[0].description + "_CPFSCrystal.archive.json"
                        # )
                        # create_archive(
                        #     CPFSBridgmanTechnique(
                        #         furnace=CPFSFurnace(
                        #             model=entry.elements[2].data_elements[1].children[0].children[0].description,
                        #         ),
                        #         crucible=CPFSCrucible(
                        #             material=entry.elements[2].data_elements[1].children[1].children[0].description,
                        #             diameter=entry.elements[2].data_elements[1].children[1].children[1].value/1000.,
                        #         ),
                        #         tube=CPFSCrystalGrowthTube(
                        #             material=entry.elements[2].data_elements[1].children[2].children[0].description,
                        #             diameter=entry.elements[2].data_elements[1].children[2].children[1].value/1000.,
                        #             filling=entry.elements[2].data_elements[1].children[2].children[2].description,
                        #         ),
                        #         steps=[CPFSBridgmanTechniqueStep(
                        #             temperature=entry.elements[5].data_elements[0].children[0].value+273.15,
                        #             pulling_rate=entry.elements[5].data_elements[0].children[1].value/1000./60.,
                        #         )],
                        #         initial_materials=materials,
                        #         resulting_crystal=crystal_ref,
                        #     ),
                        #     archive,
                        #     entry.elements[2].data_elements[0].children[0].description + "_" + entry.elements[5].data_elements[1].children[0].description + "_CPFSBridgmanTechnique.archive.json"
                        # )





m_package.__init_metainfo__()