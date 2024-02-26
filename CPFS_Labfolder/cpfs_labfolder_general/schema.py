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

import pandas as pd

import pint

from nomad.units import ureg

import importlib

import nomad.datamodel as nodm

from nomad.datamodel.metainfo.eln.labfolder import LabfolderProject

from nomad.metainfo import Package, Section, MEnum, SubSection, Quantity

from nomad.datamodel.data import (
    EntryData,
)


from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    BrowserAnnotation,
    SectionProperties,
)

from structlog.stdlib import (
    BoundLogger,
)

from nomad_material_processing.utils import (
    create_archive,
)

from nomad.datamodel.metainfo.eln import (
    Ensemble,
)

m_package = Package(name='cpfs_labfolder_general')

def clean_attribute(input_key: str) -> str:
    output_key = (
        input_key
        .split("NOMAD: ")[0]
        .lower()
        .strip()
        .replace('/ ','_')
        .replace(' ','_')
        .replace('/','_')
    )
    return output_key

class CPFSGenLabfolderProject(LabfolderProject,EntryData):

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'project_url',
                    'import_entry_id',
                    'labfolder_email',
                    'password',
                    'mapping_file',
                ],
            ),
            lane_width='800px',
        ),
    )


    import_entry_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )

    mapping_file = Quantity(
        type=str,
        description='''
        The file with the schema mapping (optional). (.dat file).
        ''',
        a_browser=BrowserAnnotation(
            adaptor='RawFileAdaptor'
        ),
        a_eln=ELNAnnotation(
            component='FileEditQuantity'
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:

        super(CPFSGenLabfolderProject, self).normalize(archive, logger)

        import re

        TAG_RE=re.compile(r'<[^>]+>')

        _selection_mapping = dict()

        if self.mapping_file:
            with archive.m_context.raw_file(self.mapping_file, 'r') as mapping:
                inp=mapping.readlines()
            for line in inp:
                if line.startswith("#") or line=="\n":
                    continue
                if len(line.split())!=3:
                    logger.warning("Found line in mapping file with wrong input. Has top be three parts.")
                    continue
                try:
                    _selection_mapping[line.split()[0]]
                    logger.warning("The key "+line.split()[0]+" is duplicate in the mapping: "+str(_selection_mapping[line.split()[0]])+" , "+line.split()[1]+"."+line.split()[2])
                    continue
                except KeyError:
                    try:
                        _selection_mapping[line.split()[0]]=getattr(importlib.import_module(line.split()[1]),line.split()[2])
                    except AttributeError:
                        logger.warning("The module "+line.split()[1]+" has no class "+line.split()[2]+".")
                        continue
                    except ModuleNotFoundError:
                        logger.warning("The module "+line.split()[1]+" was not found.")
                        continue


        if self.import_entry_id:
            for entry in self.entries:
                if str(entry.id)==str(self.import_entry_id):
                    #More general way possible?
                    possible_classes=list(set(_selection_mapping)&set(entry.tags))
                    if len(possible_classes)==0:
                        logger.warning("No suitable class found in the LabFolderEntry tags. Use one of the following: "+str(list(_selection_mapping)))
                        break
                    if len(possible_classes)>1:
                        logger.warning("Too many suitable class found in the LabFolderEntry tags. Use only one of the following: "+str(list(_selection_mapping)))
                        break
                    labfolder_section=_selection_mapping[possible_classes[0]]()
                    logger.info(possible_classes[0]+" template found.")
                    data_content=dict()
                    for element in entry.elements:
                        if element.element_type=="DATA":
                            data_content=data_content|pd.json_normalize(element.labfolder_data,sep=";;;").to_dict(orient="records")[0]
                        if element.element_type=="TEXT":
                            line=TAG_RE.sub("",element.content)
                            data_content=data_content|dict({line.split("\n")[0]+";;;description":";".join(line.split("\n")[1:])})
                        if element.element_type=="TABLE":
                            for key in element.content["sheets"]:
                                name=element.content["sheets"][key]["name"].replace("NOMAD- ","NOMAD: ")
                                if "NOMAD: " in name:
                                    table=element.content["sheets"][key]["data"]["dataTable"]
                                    df=pd.DataFrame.from_dict({(i): {(j): table[i][j]["value"]  for j in table[i].keys()} for i in table.keys()},orient="index")
                                    df.columns=df.iloc[0]
                                    df=df.iloc[1:].reset_index(drop=True)
                                    for i in range(len(df)):
                                        for key in df:
                                            if "rep per line" in name:
                                                #figure out unit
                                                unit=re.findall(r'\(.*?\)',key)
                                                if len(unit)==1:
                                                    try:
                                                        a=ureg(unit[0].strip("(").strip(")"))
                                                        data_content=data_content|dict({name.replace("per line",str(i))+";;;"+key.replace(unit[0],"")+";;;unit":unit[0].strip("(").strip(")")})
                                                        data_content=data_content|dict({name.replace("per line",str(i))+";;;"+key.replace(unit[0],"")+";;;value":df[key][i]})
                                                    except pint.errors.UndefinedUnitError:
                                                        data_content=data_content|dict({name.replace("per line",str(i))+";;;"+key.replace(unit[0],"")+";;;description":df[key][i]})
                                                elif len(unit)==0:
                                                    data_content=data_content|dict({name.replace("per line",str(i))+";;;"+key+";;;description":df[key][i]})
                                                else:
                                                    logger.warning("Could not match table entry "+key+". Too many parenthesis.")
                    subsection_list=[]
                    for key in data_content.keys():
                        if data_content[key]==None or data_content[key]=="":
                            continue
                        if "NOMAD:" in key:
                            line=key.split("NOMAD: ")[1].split(";;;")[0].strip()
                            if " rep " in line:
                                line=line.split(" rep ")[0]+" rep "
                            if not line in subsection_list:
                                subsection_list.append(line)
                        else:
                            if key.split(";;;")[-1]=="unit":
                                continue
                            attrib=clean_attribute(key.split(";;;")[-2])
                            if hasattr(labfolder_section,attrib):
                                if key.split(";;;")[-1]=="value":
                                    try:
                                        setattr(labfolder_section,attrib,ureg.Quantity(float(data_content[key]),data_content[key.strip("value")+"unit"]))
                                    except TypeError:
                                        try:
                                            setattr(labfolder_section,attrib,ureg.Quantity(int(data_content[key]),data_content[key.strip("value")+"unit"]))
                                        except TypeError as error:
                                            logger.warning("JSON entry with key "+key+" could not be parsed with error: "+str(error))
                                if key.split(";;;")[-1]=="description":
                                    try:
                                        setattr(labfolder_section,attrib,data_content[key])
                                    except Exception as error:
                                        logger.warning("JSON entry with key "+key+" could not be parsed with error: "+str(error))

                    for section in subsection_list:
                        repcount=0
                        replist=[]
                        for repcount in range(1000):
                            if " rep " in section:
                                section=section.split(" rep ")[0]+" rep "+str(repcount)
                                found=False
                            if section.startswith("Subs") or section.startswith("Arch"):
                                if not hasattr(labfolder_section,section.split(" ")[2]):
                                    logger.warning("The schema does not have a Subsection "+section.split(" ")[1])
                                    break
                                if section.startswith("Subs"):
                                    logger.info("Creating Subsection "+section.split(" ")[1])
                                if section.startswith("Arch"):
                                    logger.info("Creating Archive "+section.split(" ")[1])
                                section_object=_selection_mapping[section.split(" ")[1]]()
                                for key in data_content.keys():
                                    if data_content[key]==None or data_content[key]=="":
                                        continue
                                    if "NOMAD: " in key and section in key:
                                        found=True
                                        if key.split(";;;")[-1]=="unit":
                                            continue
                                        attrib=clean_attribute(key.split(";;;")[-2])
                                        if hasattr(section_object,attrib):
                                            if key.split(";;;")[-1]=="value":
                                                try:
                                                    setattr(section_object,attrib,ureg.Quantity(float(data_content[key]),data_content[key.strip("value")+"unit"]))
                                                except TypeError:
                                                    try:
                                                        setattr(section_object,attrib,ureg.Quantity(int(data_content[key]),data_content[key.strip("value")+"unit"]))
                                                    except TypeError as error:
                                                        logger.warning("JSON entry with key "+key+" could not be parsed with error: "+str(error))
                                            if key.split(";;;")[-1]=="description":
                                                try:
                                                    setattr(section_object,attrib,data_content[key])
                                                except Exception as error:
                                                    logger.warning("JSON entry with key "+key+" could not be parsed with error: "+str(error))

                                if section.startswith("Arch"):
                                    section_object = create_archive(
                                            section_object,
                                            archive,
                                            entry.title + "_" + entry.id + "_"+section.split(" ")[1]+".archive.json"
                                        )

                            if found==True:
                                replist.append(section_object)
                            if found==False or not " rep " in section:
                                break

                        if not " rep " in section:
                            setattr(labfolder_section,section.split(" ")[2],replist[0])
                        else:
                            setattr(labfolder_section,section.split(" ")[2],replist)


                    create_archive(
                            labfolder_section,
                            archive,
                            entry.title + "_" + entry.id + "_"+possible_classes[0]+".archive.json"
                        )


m_package.__init_metainfo__()
