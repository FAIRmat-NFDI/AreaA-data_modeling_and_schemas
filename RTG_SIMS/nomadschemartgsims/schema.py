from nomad.metainfo import Quantity, Package, SubSection, MEnum, Section
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.eln import Measurement
from nomad.units import ureg
import numpy as np

m_package = Package()

class DepthProfile(ArchiveSection):#, repeats=True):
    m_def = Section(
        a_eln=dict(lane_width='600px'),
        a_plot={'label': 'SIMS profile','x': 'depth', 'y': 'intensity'
        })
    element = Quantity(
        type=str,
        description='Method used to collect the data',
        a_plot={
            'label': 'SIMS profile','x': 'depth', 'y': 'intensity'
        })
        
    depth = Quantity(
        type=np.dtype(np.float64),
        unit = "µm",
        shape = ['*'],
        a_plot={
            'label': 'SIMS profile','x': 'depth', 'y': './intensity'
        })
    intensity = Quantity(
        type=np.dtype(np.float64),
        unit = "1/s",
        shape = ['*'],
        a_plot={
           'label': 'SIMS profile', 'x': 'depth', 'y': 'intensity'
        })

class RTGSIMS(Measurement):
    '''
    X-ray diffraction is a technique typically used to characterize the structural
    properties of crystalline materials. The data contains `two_theta` values of the scan
    the corresponding counts collected for each channel
    '''
    method = Quantity(
        type=str,
        description='Method used to collect the data',
        default='SIMS')
    depth_profile_ID = Quantity(
        type=str,
        description='depth profile ID from RTG')
    Matrix = Quantity(
        type=str,
        description='Element Matrix for Mass Spectrometer')
    SampleID = Quantity(
        type=str,
        description='IKZ sampleID, make use of sample ID class!')
    depth_profiles = SubSection(section_def=DepthProfile, repeats=True)
   

class RTG_SIMS_measurement(RTGSIMS, EntryData):
    m_def = Section(
        a_eln=dict(lane_width='600px'),
        a_plot={'x': 'depth', 'y': 'intensity'
        })
    
    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity))
    message = Quantity(type=str)
    data_file = Quantity(
        type=str,
        description='Data file containing the RTG depth profile SIMS dat (dp_ascii)',
        a_eln=dict(
            component='FileEditQuantity',
        )
        )


    def normalize(self, archive, logger):
        super(RTG_SIMS_measurement, self).normalize(archive, logger)
        logger.info('ExampleSection.normalize called')

        def parse_depthprofile_data(self):
            #with open (fp, "rt") as f:
            data = self.readlines()
            Zn_counter = 0 # this is particular for FBH data where different Zn ions were measured
            element = None
            measurement_counter=0
            depth_profiles=[]
            unit = None
            sims_dict= {}
            for line in data:
                if "DEPTH PROFILE :" in line:
                    depth_profile_id = (line.split(":")[1]).strip()
                    sims_dict=dict(depth_profile_id=depth_profile_id)
                elif "Date" in line:
                    date = (line.split(":")[1]).strip()
                    sims_dict.update(dict(date=date))
                elif "Matrix" in line:
                    matrix = (line.split(":")[1]).strip()
                    sims_dict.update(dict(Matrix=matrix))
                elif "Sample name" in line:
                    sample_id = (line.split(":")[1]).strip()
                    sims_dict.update(dict(sample_id=sample_id))         
                elif "ELEMENT" in line:
                    element = (line.split("T ")[1]).strip("\n")
                    measurement_counter=+1
                    if element == "Zn":
                        Zn_counter += 1
                        element += str(Zn_counter)
                    element_dict = dict(element=element, depth=[], intensity=[], unit=None)
                elif "points" in line:
                    points=(int(line.split(" points")[0]))
                    points_counter=0
                elif "[um]" in line:
                    unit = line.split("] ")[1].strip()
                    element_dict["unit"]=unit
                elif "E+" in line or "E-" in line:
                    points_counter+=1
                    element_dict["depth"].append(float(line.split("      ")[0].strip()))
                    element_dict["intensity"].append(float(line.split("      ")[1].strip()))
                    if points_counter == points :
                        depth_profiles.append(element_dict)
                        points_counter = 0
                        element_dict= {}
            sims_dict.update(dict(depth_profiles_of_elements=depth_profiles))
            return sims_dict

        #if not self.data_file:
        #    return
        if archive.data.data_file:
            with archive.m_context.raw_file(self.data_file) as file:
                sims_dict=parse_depthprofile_data(file)
                self.Matrix = sims_dict["Matrix"]
                #self.datetime = sims_dict["Date"] # noch in richtiges FOrmat ändern
                self.SampleID = sims_dict["sample_id"]
                self.lab_id = sims_dict["depth_profile_id"]
                self.depth_profile_ID = sims_dict["depth_profile_id"]
                logger.info('parser works')
                self.depth_profiles=[]
                #dep_profile_object=DepthProfile()
                for count,value in enumerate(sims_dict["depth_profiles_of_elements"]):
                    dep_profile_object=DepthProfile()
                    dep_profile_object.element = sims_dict["depth_profiles_of_elements"][count]["element"]
                    dep_profile_object.depth = sims_dict["depth_profiles_of_elements"][count]["depth"]
                    dep_profile_object.intensity = sims_dict["depth_profiles_of_elements"][count]["intensity"]
                    self.depth_profiles.append(dep_profile_object)
        #self.message = f'Hello {self.name}!'


m_package.__init_metainfo__()
