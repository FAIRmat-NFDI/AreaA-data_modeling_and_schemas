# -*- coding: utf-8 -*-
"""
@author: kernke
"""
import json
import numpy as np
import cv2
import os
import base64



instrument="nomad.datamodel.metainfo.basesections.Instrument"
measurement="nomad.datamodel.metainfo.basesections.Measurement"
sample="nomad.datamodel.metainfo.basesections.CompositeSystem"
process="nomad.datamodel.metainfo.basesections.Process"

type_lut=dict()
type_lut["np.float64"]="NumberEditQuantity"
type_lut["int"]="NumberEditQuantity"
type_lut["str"]="StringEditQuantity"
type_lut["string"]="RichTextEditQuantity" #url maybe, if it works
type_lut["bool"]="BoolEditQuantity"
type_lut["Datetime"]="DateTimeEditQuantity"
type_lut[instrument]="ReferenceEditQuantity"
type_lut[sample]="ReferenceEditQuantity"
type_lut[measurement]="ReferenceEditQuantity"
type_lut[process]="ReferenceEditQuantity"


instrument_dict=dict()
instrument_dict["Apreo"]='../upload/raw/Instruments/Apreo_SEM.archive.yaml#data'
instrument_dict["Apreo/T1"]='../upload/raw/Instruments/Apreo_T1.archive.yaml#data'
instrument_dict["Apreo/T2"]='../upload/raw/Instruments/Apreo_T2.archive.yaml#data'
instrument_dict["Apreo/T3"]='../upload/raw/Instruments/Apreo_T3.archive.yaml#data'
instrument_dict["Apreo/ETD"]='../upload/raw/Instruments/Apreo_ETD.archive.yaml#data'
instrument_dict["Apreo/CL"]='../upload/raw/Instruments/Apreo_Monarc_Spectrometer.archive.yaml#data'

#%% general utility

def add_section(yt,name,quantity_type_unit_list,object_type=None,hide_list=None,indentation_level=2,
                sub_section=False,default_unit_list=None,type_lut=type_lut):
    
    if default_unit_list is None:
        default_unit_list=[None for i in range(len(quantity_type_unit_list))]
    
    qtu=quantity_type_unit_list
    w=indentation_level*2
    yt += w*" "+name + ":\n"
    if sub_section:
        w+=2
        yt+= w*" " + "section:\n" 
        extra=2
    else:
        extra=0
    w+=2
    yt+= w*" " + "base_sections:\n"
    w+=2
    if object_type is None:
        pass
    else:
        yt+= w*" " + "- nomad.datamodel.metainfo.basesections."+object_type+"\n"
    yt+= w*" " + "- nomad.datamodel.data.EntryData\n"
    w-=2
    yt+= w*" " + "m_annotations:\n"
    w+=2
    yt+= w*" " + "eln:\n"
    w+=2
    if hide_list is None:
        pass
    else:
        yt+= w*" " + "hide: "+str(hide_list)+"\n"
    w = indentation_level*2+2+extra
    
    if len(qtu)>0:
        yt+= w*" " + "quantities:\n"
    
    for i in range(len(qtu)):
        w = indentation_level*2+4+extra
        yt+= w*" " + qtu[i][0] +":\n"
        w+=2
        yt+= w*" " + "type: "+qtu[i][1]+"\n"
        if len(qtu[i])>3:
            yt+= w*" " + "shape: "+qtu[i][3]+"\n"
        
        if qtu[i][2] is None:
            yt+= w*" " + "m_annotations:\n"
            w+=2
            yt+=w*" " + "eln:\n"
            w+=2
        else:
            yt+= w*" " + "unit: "+qtu[i][2]+"\n"
            yt+= w*" " + "m_annotations:\n"
            w+=2
            yt+=w*" " + "eln:\n"
            w+=2
            if default_unit_list[i] is None:
                yt+=w*" " + "defaultDisplayUnit: "+qtu[i][2]+"\n"
            else:
                yt+=w*" " + "defaultDisplayUnit: "+default_unit_list[i]+"\n"
        yt+=w*" " + "component: "+type_lut[qtu[i][1]]+"\n"
        
    return yt    


       
def schema_start(schema_name):
    yaml_text=""
    yt=yaml_text
    yt += "definitions:\n"
    yt += 2*" "+"name: " + schema_name+"\n"
    yt += 2*" "+"sections:\n"
    return yt


def read_schema(filepath):
    "only for schemas with a depth of: sections, section-quantities, subsections,subsection-quantities"
    with open(filepath, 'r') as fp:
        lines=fp.readlines()
    w4="    "
    w1=" "
    w10="          "
    sections=dict()
    for c,i in enumerate(lines):
        if i[:4]==w4:
            end=i.find(":")
            if i[4] != w1:
                selected_section=i[4:end]
                selected_subsection=None
                sections[selected_section]=dict()
                sections[selected_section]["quantities"]=[]
                sections[selected_section]["sub_sections"]=dict()
                
            elif i[4:8]==w4 and i[9] != w1:
                if i[8:end] !="eln" and i[8:end] !="browser" :
                    if "sub_section" in lines[c-1]:
                        selected_subsection=i[8:end]
                        sections[selected_section]["sub_sections"][selected_subsection]=dict()
                        sections[selected_section]["sub_sections"][selected_subsection]["quantities"]=[]
                        
                    else:
                        sections[selected_section]["quantities"].append(i[8:end])
            elif selected_subsection is not None and i[4:14]==w10 and i[15] != w1:
                if i[14:end] != "eln" and i[14:end] != "browser":
                    sections[selected_section]["sub_sections"][selected_subsection]["quantities"].append(i[14:end])
    return sections

def save_schema(schema_name,yt):
    directory="../Schemas/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory+schema_name+ ".archive.yaml", "w") as text_file:
        text_file.write(yt)



def save_instrument(name,yt):
    directory="../Instruments/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory+name+ ".archive.yaml", "w") as text_file:
        text_file.write(yt)

def save_sample(name,yt):
    directory="../Samples/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory+name+ ".archive.yaml", "w") as text_file:
        text_file.write(yt)


#%% specialized utility

def get_metadata_tif(filepath):
    with open(filepath, 'r', encoding="utf8",errors="ignore") as fp:
        contents=fp.read()    
    text=contents[contents.find("Date"):]
    # qtu <-- quantitiy_type_unit
    #Beam
    qtu=[["\nSystemType=","str",None],
         ["\nTimeOfCreation=","str",None],
         
         ["\nPixelWidth=","np.float64","m"],
         ["\nPixelHeight=","np.float64","m"],         
    #Microscope     
         ["\nHV=","np.float64","V"],
         ["\nBeamCurrent=","np.float64","A"],
         ["\nWorkingDistance=","np.float64","m"],
         ["\nDwelltime=","np.float64","s"],
         
         ["\nSpot=","np.float64","nm"],
         ["\nStigmatorX=","np.float64",None],
         ["\nStigmatorY=","np.float64",None],
         ["\nBeamShiftX=","np.float64",None],
         ["\nBeamShiftY=","np.float64",None],
         ["\nSourceTiltX=","np.float64",None],
         ["\nSourceTiltY=","np.float64",None],
         ["\nEmissionCurrent=","np.float64","A"],
         ["\nSpecimenCurrent=","np.float64","A"],
         #["\nApertureDiameter=","np.float64","m"],
         #["\nATubeVoltage=","np.float64","V"],
    #Scan     
         ["\nUseCase=","str",None],
         ["\nTiltCorrectionIsOn=","str",None],#yes,no 
         
         ["\nScanRotation=","np.float64","rad"],


    #CompoundLens
         ["\nIsOn=","str",None], #On,Off
         ["\nThresholdEnergy=","np.float64","eV"],
    #Stage          
         ["\nStageX=","np.float64","m"],
         ["\nStageY=","np.float64","m"],
         ["\nStageZ=","np.float64","m"],
         ["\nStageR=","np.float64","rad"],
         ["\nStageTa=","np.float64","rad"],
         ["\nStageTb=","np.float64","rad"],
         ["\nStageBias=","np.float64","V"],
         ["\nChPressure=","np.float64","Pa"],

    #Detecor
         ["\nName=","str",None],
         ["\nMode=","str",None],
         
         ["\nSignal=","str",None],
         ["\nContrast=","np.float64",None],
         ["\nBrightness=","np.float64",None],
         ["\nContrastDB=","np.float64","dB"],
         ["\nBrightnessDB=","np.float64","dB"],
         ["\nAverage=","int",None],
         ["\nIntegrate=","int",None],
         ["\nResolutionX=","int",None],
         ["\nResolutionY=","int",None],
         ["\nHorFieldsize=","np.float64","m"],
         ["\nVerFieldsize=","np.float64","m"],
         ["\nFrameTime=","np.float64","s"],
    #Digital
         ["\nDigitalContrast=","np.float64",None],
         ["\nDigitalBrightness=","np.float64",None],
         ["\nDigitalGamma=","np.float64",None]]
    
    res=[]
    
    typechanges=[]
    counter=0
    for i in qtu:
        kw=i[0]
        start=text.find(kw)+len(kw)
        end=text[start:].find("\n")
        if i[1]=="int":    
            res.append(int(text[start:start+end]))
        elif i[1]=="np.float64":
            res.append(np.double(text[start:start+end]))
        elif i[1]=="str" or i[1]=="string":
            if text[start:start+end] in ["no","No","off","Off","false","False"]:
                res.append(False)
                typechanges.append(counter)
            elif text[start:start+end] in ["yes","Yes","on","On","true","True"]:
                res.append(True)
                typechanges.append(counter)
            elif ":" in text[start:start+end]:
                datestring=text[start:start+end]
                
                datestring=datestring.replace("."," ")
                day,month,year,hour=datestring.split(" ")
                newdate=year+"-"+month+"-"+day+" "+hour
                newdate +=".000Z"
                res.append(newdate)
            else:
                res.append(text[start:start+end])
        counter +=1

    for j in typechanges:
        qtu[j][1]="bool"
    

    res.append(os.path.abspath(filepath).replace("\\","/"))
    qtu.append(["PathToImage","str",None])
               
    qtu_dict=readable_names(res,qtu)
    return qtu_dict


def readable_names(res,qtu):
    
    nice_names=dict()

    nice_names["\nSystemType="]="Microscope"
    nice_names["\nTimeOfCreation="]="Time_of_Creation" 
    nice_names["\nPixelWidth="]="Pixel_Width"
    nice_names["\nPixelHeight="]="Pixel_Height"
    nice_names["\nHV="]="Acceleration_Voltage"
    nice_names["\nBeamCurrent="]="Beam Current"
    nice_names["\nWorkingDistance="]="Working_Distance"
    nice_names["\nDwelltime="]="Dwell_Time"
    nice_names["\nSpot="]="Spot_Diameter_(estimated)"    
    nice_names["\nStigmatorX="]="Stigmator_X"
    nice_names["\nStigmatorY="]="Stigmator_Y"
    nice_names["\nBeamShiftX="]="Beam_Shift_X"
    nice_names["\nBeamShiftY="]="Beam_Shift_Y"
    nice_names["\nSourceTiltX="]="Source_Tilt_X"
    nice_names["\nSourceTiltY="]="Source_Tilt_Y"
    nice_names["\nEmissionCurrent="]="Emission_Current"
    nice_names["\nSpecimenCurrent="]="Specimen_Current"
    nice_names["\nUseCase="]="SEM_Mode"
    nice_names["\nTiltCorrectionIsOn="]="Tilt_Correction"
    nice_names["\nScanRotation="]="Scan_Rotation"
    nice_names["\nIsOn="] ="Compound_Lens"           
    nice_names["\nThresholdEnergy="]="Compound_Lens_Threshold_Energy"            
    nice_names["\nStageX="]="Stage_X"            
    nice_names["\nStageY="]="Stage_Y"            
    nice_names["\nStageZ="]="Stage_Z"
    nice_names["\nStageR="]="Stage_Rotation"
    nice_names["\nStageTa="]="Stage_Tilt_alpha"
    nice_names["\nStageTb="]="Stage_Tilt_beta"
    nice_names["\nStageBias="]="Stage_Bias"
    nice_names["\nChPressure="]="Chamber_Pressure"
    nice_names["\nName="]="Detector"
    nice_names["\nMode="]="Detector_Mode"
    nice_names["\nSignal="]="Signal_Type"
    nice_names["\nContrast="]="Contrast"
    nice_names["\nContrastDB="]="Contrast_DB"
    nice_names["\nBrightness="]="Brightness"
    nice_names["\nBrightnessDB="]="Brightness_DB"
    nice_names["\nAverage="]="Average"
    nice_names["\nIntegrate="]="Integrate"
    nice_names["\nResolutionX="]="Resolution_X"
    nice_names["\nResolutionY="]="Resolution_Y"
    nice_names["\nHorFieldsize="]="Horizontal_Fieldsize"
    nice_names["\nVerFieldsize="]="Vertical_Fieldsize"
    nice_names["\nFrameTime="]="Frame_Time"
    nice_names["\nDigitalContrast="]="Digital_Contrast"
    nice_names["\nDigitalBrightness="]="Digital_Brightness"
    nice_names["\nDigitalGamma="]="Digital_Gamma"
    nice_names["PathToImage"]="Path_to_Image"
    

    qtu_dict=dict()       
    for i in range(len(qtu)):
        qtu_dict[nice_names[qtu[i][0]]]=qtu[i][1:]
        qtu_dict[nice_names[qtu[i][0]]].append(res[i])
        #qtu[i][0]=nice_names[qtu[i][0]]
    return qtu_dict
    
    
def create_data_json(filepath,schemapath,data_name,nomad_sample_paths=None,instrument_dict=instrument_dict):    

    
    img=cv2.imread(filepath,0)
    h=420
    height=img.shape[0]
    scale_factor=height / h
    preview=cv2.resize(img,[int(img.shape[1]//scale_factor),h],cv2.INTER_AREA)
    cv2.imwrite("temporary_file.png",preview)
    with open("temporary_file.png", "rb") as f:
        encoded_image = base64.b64encode(f.read())
    os.remove("temporary_file.png")
    
    data_json=dict()
    data_json["data"]=dict()
    data_json["data"]["m_def"]="../upload/raw/Schemas/Data_Entries.archive.yaml#/definitions/section_definitions/0"
    data_json["data"]["description"]='<p><img src=\"data:image/png;base64,'
    data_json["data"]["description"]+=str(encoded_image)[2:-1]
    data_json["data"]["description"]+='\" /></p>"'
    data_json["data"]["description"]=data_json["data"]["description"][:-1]
    
    if nomad_sample_paths is not None and not isinstance(nomad_sample_paths, list):
        nomad_sample_paths=[nomad_sample_paths]
    
    
    sections=read_schema(schemapath)
    qtu_dict=get_metadata_tif(filepath)
    #qtu_di
    quantities=sections["SEM_Image"]["quantities"]
    subquantities=sections["SEM_Image"]["sub_sections"]["Meta_Data"]["quantities"]
    
    for i in quantities:
        if i == "Sample":
            if nomad_sample_paths is None:
                pass
            else:
                samplelist=[]
                for j in nomad_sample_paths:
                    samplelist.append("../upload/raw/"+j+"#data")
                data_json["data"][i]=samplelist
        elif i=="Microscope":
            if qtu_dict[i][-1]=="Apreo":
                microsc="Apreo"
                data_json["data"][i]=instrument_dict["Apreo"]
            else:
                pass
        elif i=="Detector":
            if microsc=="Apreo":
                detstring="Apreo/"+qtu_dict[i][-1]
                data_json["data"][i]=instrument_dict[detstring]
            else:
                pass
            
        else:
            data_json["data"][i]=qtu_dict[i][-1]
    
    if len(subquantities)>0:
        data_json["data"]["Meta_Data"]=dict()
    
        for i in subquantities:
            data_json["data"]["Meta_Data"][i]=qtu_dict[i][-1]
    
    
    
    directory="../Database_jsons/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath=directory+data_name+".archive.json" 
    with open(filepath, 'w') as fp:
        json.dump(data_json, fp)
    #return qtu_dict
