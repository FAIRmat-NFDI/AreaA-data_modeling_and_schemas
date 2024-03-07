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
        import json

        TAG_RE=re.compile(r'<[^>]+>')

        _selection_mapping = dict()

        if self.mapping_file:
            with archive.m_context.raw_file(self.mapping_file, 'r') as mapping:
                inp=json.load(mapping)
            for cl in inp["Classes"].keys():
                try:
                    _selection_mapping[cl]=getattr(importlib.import_module(".".join(inp["Classes"][cl]["class"].split(".")[:-1])),inp["Classes"][cl]["class"].split(".")[-1])
                except AttributeError:
                    logger.warning("The module "+".".join(inp["Classes"][cl]["class"].split(".")[:-1])+" has no class "+inp["Classes"][cl]["class"].split(".")[-1]+".")
                    continue
                except ModuleNotFoundError:
                    logger.warning("The module "+".".join(inp["Classes"][cl]["class"].split(".")[:-1])+" was not found.")
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
                    table_content=[]
                    text_content=dict()
                    for element in entry.elements:
                        if element.element_type=="DATA":
                            data_content=data_content|element.labfolder_data
                        if element.element_type=="TEXT":
                            text_content=text_content|dict({TAG_RE.sub("",element.content.split("</p>")[0]):TAG_RE.sub("",";".join(element.content.split("</p>")[1:]))})
                        if element.element_type=="TABLE":
                            for key in element.content["sheets"]:
                                table=element.content["sheets"][key]["data"]["dataTable"]
                                df=pd.DataFrame.from_dict({(i): {(j): table[i][j]["value"]  for j in table[i].keys()} for i in table.keys()},orient="index")
                                df.columns=df.iloc[0]
                                df=df.iloc[1:].reset_index(drop=True)
                                df=df.to_dict(orient="index")
                                df["name"]=element.title
                                table_content.append(df)


                    for section in inp["Classes"].keys():
                        logger.info(section)
                        replist=[]
                        for repcount in range(10):
                            found=True
                            if (inp["Classes"][section]["repeats"]=="false" or inp["Classes"][section]["repeats"]=="true") and repcount>0:
                                continue
                            if inp["Classes"][section]["type"]=="SubSection" or inp["Classes"][section]["type"]=="Archive" or inp["Classes"][section]["type"]=="main":
                                if not hasattr(labfolder_section,inp["Classes"][section]["attribute"]) and not inp["Classes"][section]["type"]=="main":
                                    logger.warning("The schema does not have an attribute "+inp["Classes"][section]["attribute"])
                                    break
                                if inp["Classes"][section]["type"]=="SubSection":
                                    logger.info("Creating Subsection "+section)
                                if inp["Classes"][section]["type"]=="Archive":
                                    logger.info("Creating Archive "+section)
                                if inp["Classes"][section]["type"]=="main":
                                    section_object=labfolder_section
                                else:
                                    section_object=getattr(importlib.import_module(".".join(inp["Classes"][section]["class"].split(".")[:-1])),inp["Classes"][section]["class"].split(".")[-1])()

                                #TODO: find better way of interating through a json
                                maps=inp["Mapping"]["Data elements"]
                                for key1 in maps:
                                    if "object" in maps[key1]:
                                        if maps[key1]["object"]==section:
                                            try:
                                                setattr(section_object,maps[key1]["key"],ureg.Quantity(float(data_content[key1]["value"]),data_content[key1]["unit"]))
                                            except Exception:
                                                try:
                                                    setattr(section_object,maps[key1]["key"],data_content[key1]["description"])
                                                except Exception as error:
                                                    logger.warning("JSON entry with key "+key1+" could not be parsed with error: "+str(error))
                                                    continue
                                            continue
                                    maps1=maps[key1]
                                    for key2 in maps1:
                                        if "object" in maps1[key2]:
                                            if maps1[key2]["object"]==section:
                                                try:
                                                    setattr(section_object,maps1[key2]["key"],ureg.Quantity(float(data_content[key1][key2]["value"]),data_content[key1][key2]["unit"]))
                                                except Exception:
                                                    try:
                                                        setattr(section_object,maps1[key2]["key"],data_content[key1][key2]["description"])
                                                    except Exception as error:
                                                        logger.warning("JSON entry with key "+key1+key2+" could not be parsed with error: "+str(error))
                                                        continue
                                                continue
                                        maps2=maps1[key2]
                                        for key3 in maps2:
                                            if "object" in maps2[key3]:
                                                if maps2[key3]["object"]==section:
                                                    try:
                                                        setattr(section_object,maps2[key3]["key"],ureg.Quantity(float(data_content[key1][key2][key3]["value"]),data_content[key1][key2][key3]["unit"]))
                                                    except Exception:
                                                        try:
                                                            setattr(section_object,maps2[key3]["key"],data_content[key1][key2][key3]["description"])
                                                        except Exception as error:
                                                            logger.warning("JSON entry with key "+key1+key2+key3+" could not be parsed with error: "+str(error))
                                                            continue
                                                    continue

                                maps=inp["Mapping"]["Text elements"]
                                for key1 in maps:
                                    if maps[key1]["object"]==section:
                                        try:
                                            setattr(section_object,maps[key1]["key"],text_content[key1])
                                        except Exception as error:
                                            logger.warning("Text entry with key "+key1+" could not be parsed with error: "+str(error))

                                maps=inp["Mapping"]["Table elements"]
                                for key1 in maps:
                                    for table in table_content:
                                        if table["name"]==key1:
                                            try:
                                                line=table[repcount]
                                                for key2 in maps[key1]:
                                                    try:
                                                        setattr(section_object,maps[key1][key2]["key"],line[key2])
                                                    except Exception as error:
                                                        logger.warning("Text entry with key "+key1+key2+" could not be parsed with error: "+str(error))

                                            except KeyError:
                                                found=False

                                if inp["Classes"][section]["name"]!="":
                                    temp=inp["Classes"][section]["name"]
                                    name=""
                                    for line in temp.split("+"):
                                        if line.startswith("LF"):
                                            if line.startswith("LF.data"):
                                                add=data_content
                                                for i in range(len(line.split("."))-2):
                                                    add=add[line.split(".")[i+2]]
                                                name=name+add["description"]
                                        else:
                                            name=name+line

                                    section_object.name=name

                                if inp["Classes"][section]["type"]=="Archive":

                                    section_object = create_archive(
                                            section_object,
                                            archive,
                                            name
                                        )

                                if found or repcount==0:
                                    replist.append(section_object)
                                logger.info(section,repcount,replist)

                        if not inp["Classes"][section]["type"]=="main":
                            if inp["Classes"][section]["repeats"]=="false":
                                setattr(labfolder_section,inp["Classes"][section]["attribute"],replist[0])
                            else:
                                setattr(labfolder_section,inp["Classes"][section]["attribute"],replist)



                    temp=inp["Classes"][possible_classes[0]]["name"]
                    name=""
                    for line in temp.split("+"):
                        if line.startswith("LF"):
                            if line.startswith("LF.data"):
                                add=data_content
                                for i in range(len(line.split("."))-2):
                                    add=add[line.split(".")[i+2]]
                                name=name+add["description"]
                        else:
                            name=name+line

                    labfolder_section.name=name

                    create_archive(
                            labfolder_section,
                            archive,
                            name
                        )


m_package.__init_metainfo__()
