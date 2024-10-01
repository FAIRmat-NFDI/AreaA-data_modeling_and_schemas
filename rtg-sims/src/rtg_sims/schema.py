from nomad.metainfo import Quantity, SchemaPackage, SubSection, MEnum, Section
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.eln import Measurement, Substance, SampleID, System
from nomad.datamodel.metainfo.basesections import (
    CompositeSystemReference,
    InstrumentReference,
)
from nomad.units import ureg
from nomad.config import config
import numpy as np
from datetime import datetime


configuration = config.get_plugin_entry_point("rtg_sims:schema")

m_package = SchemaPackage()


class DepthProfileQuantitative(ArchiveSection):
    m_def = Section(
        a_eln=dict(lane_width="600px"),
        label_quantity="element",
        # a_plot={'label': 'SIMS profile','x': 'depth', 'y': 'intensity'}
    )
    element = Quantity(
        type=str,
        description="element which was measured by the mass spectrometer",
        # a_plot={
        #    'label': 'SIMS profile','x': 'depth', 'y': 'intensity'}
    )
    depth = Quantity(
        type=np.dtype(np.float64),
        description="depth of the measurement profile",
        unit="µm",
        shape=["n_values"],
        # a_plot={
        #    'x': 'depth', 'y': 'atomic_concentration'
        # })
        # a_plot={
        #   'label': 'SIMS profile','x': 'depth', 'y': './intensity'        }
    )
    atomic_concentration = Quantity(
        type=np.dtype(np.float64),
        description="Atomic concentration of the respective element by calibrated measurements. See SIMS report in RTG SIMS experiment entry for details on the calibration standard.",
        unit="1/cm^3",
        shape=["n_values"],
        a_plot={
            "x": "depth",
            "y": "./atomic_concentration",
            "layout": {"yaxis": {"type": "log"}},
        },
    )
    # a_plot={
    #  'label': 'SIMS profile', 'x': 'depth', 'y': 'intensity'        }
    #   )


class DepthProfileQualitative(ArchiveSection):  # , repeats=True):
    m_def = Section(
        a_eln=dict(lane_width="600px"),
        label_quantity="element",
        # a_plot={'label': 'SIMS profile','x': 'depth', 'y': 'intensity'}
    )
    element = Quantity(
        type=str,
        description="element which was measured by the mass spectrometer",
        # a_plot={
        #    'label': 'SIMS profile','x': 'depth', 'y': 'intensity'}
    )

    depth = Quantity(
        type=np.dtype(np.float64),
        description="depth of the measurement profile",
        unit="µm",
        shape=["n_values"],
        # a_plot={
        #    'x': 'depth', 'y': 'intensity'
        # })
        # a_plot={
        #   'label': 'SIMS profile','x': 'depth', 'y': './intensity'        }
    )
    intensity = Quantity(
        type=np.dtype(np.float64),
        description="Intensity measured by the mass spectrometer without calibration of the measured signal to an element. Serves for qualitative depth profile measurement.",
        unit="1/s",
        shape=["n_values"],
        a_plot={
            "x": "depth",
            "y": "./intensity",
            "layout": {"yaxis": {"type": "log"}},
        },
    )
    # a_plot={
    #  'label': 'SIMS profile', 'x': 'depth', 'y': 'intensity'        }
    #   )


class MeasurementResults(ArchiveSection):
    depth_profiles_qualitative = SubSection(
        section_def=DepthProfileQualitative, repeats=True
    )
    depth_profiles_quantitative = SubSection(
        section_def=DepthProfileQuantitative, repeats=True
    )


class RTGSIMS(Measurement):
    """
    The secondary ion mass spectrometry is one of the established material analysis
    techniques. For generating concentration depth profiles of elements SIMS is used as a
    standard method. Investigations close to the surface set typical range of 5 nm to 20 µm
    and a lateral range from 50 µm up to 500 µm. The determination of concentrations
    (quantitative analyses) of all elements in the mass range from hydrogen to uran allow
    a valuation of the material quality of solids. In addition to depth profiles surface
    images with a lateral solution up to the µm range facilitates an topografical valuation
    of the material structure. Additionally, it is possible to determine the spacial
    element distribution and make it visible by imaging techniques. Using the Cameca
    spectrometers it is possible to determine elements in concentrations in ranges of ppb.
    https://www.rtg-berlin.de/
    """

    method = Quantity(
        type=str, description="Method used to collect the data", default="SIMS"
    )
    Matrix = Quantity(
        type=str,  # SimsMatrix
        description="Element Matrix for Mass Spectrometer",
    )
    location = Quantity(
        type=str,
        description="""
        The location of the process in longitude, latitude.
        """,
        default="52.431685, 13.526855",
    )  # IKZ coordinates
    results = SubSection(section_def=MeasurementResults, label="Results")


class RTGSIMSMeasurement(RTGSIMS, EntryData):
    m_def = Section(
        a_eln=dict(lane_width="600px"),
        a_plot=[
            {  #'label': 'SIMS depth profile',
                "x": [
                    "results/:/depth_profiles_qualitative/:/depth",
                    "results/:/depth_profiles_quantitative/:/depth",
                ],
                "y": [
                    "results/:/depth_profiles_qualitative/:/intensity",
                    "results/:/depth_profiles_quantitative/:/atomic_concentration",
                ],
                "layout": {
                    "yaxis": {"type": "log"},
                    "yaxis2": {"type": "log"},
                    "showlegend": "true",
                },  # makes only one yaxis log scale!
            },
        ],
        a_template=dict(
            instruments=[dict(name="RTG SIMS", lab_id="RTG Mikroanalyse Cameca IMS")],
        ),
    )

    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )
    data_file = Quantity(
        type=str,
        description="Data file containing the RTG depth profile SIMS dat (dp_ascii)",
        a_eln=dict(
            component="FileEditQuantity",
        ),
    )

    def normalize(self, archive, logger):
        # super(RTGSIMSMeasurement, self).normalize(archive, logger)
        logger.info("ExampleSection.normalize called")

        def parse_depthprofile_data(self):
            # with open (fp, "rt") as f:
            data = self.readlines()
            Zn_counter = 0  # this is particular for FBH data where different Zn ions were measured
            element = None
            measurement_counter = 0
            depth_profiles_qual = []
            depth_profiles_quant = []
            unit = None
            sims_dict = {}
            for line in data:
                if "DEPTH PROFILE :" in line:
                    depth_profile_id = (line.split(":")[1]).strip()
                    sims_dict = dict(depth_profile_id=depth_profile_id)
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
                    measurement_counter = +1
                    if element == "Zn":
                        Zn_counter += 1
                        element += str(Zn_counter)
                    # element_dict = dict(element=element, depth=[], intensity=[], unit=None)
                elif "points" in line:
                    points = int(line.split(" points")[0])
                    points_counter = 0
                elif "[c/s]" in line:
                    element_dict = dict(
                        element=element, depth=[], intensity=[], unit=None
                    )
                    unit = line.split("] ")[1].strip()
                    element_dict["unit"] = unit
                    depth_profile_type = "qual"
                elif "[Atom/cm3]" in line:
                    element_dict = dict(
                        element=element, depth=[], atomic_concentration=[], unit=None
                    )
                    unit = line.split("] ")[1].strip()
                    element_dict["unit"] = unit
                    depth_profile_type = "quant"
                elif "E+" in line or "E-" in line:
                    points_counter += 1
                    if depth_profile_type == "qual":
                        element_dict["depth"].append(
                            float(line.split("      ")[0].strip())
                        )
                        element_dict["intensity"].append(
                            float(line.split("      ")[1].strip())
                        )
                        if points_counter == points:
                            depth_profiles_qual.append(element_dict)
                            points_counter = 0
                            element_dict = {}
                    if depth_profile_type == "quant":
                        element_dict["depth"].append(
                            float(line.split("      ")[0].strip())
                        )
                        element_dict["atomic_concentration"].append(
                            float(line.split("      ")[1].strip())
                        )
                        if points_counter == points:
                            depth_profiles_quant.append(element_dict)
                            points_counter = 0
                            element_dict = {}
            sims_dict.update(dict(depth_profiles_of_elements_qual=depth_profiles_qual))
            sims_dict.update(
                dict(depth_profiles_of_elements_quant=depth_profiles_quant)
            )
            return sims_dict

        # if not self.data_file:
        #    return
        if archive.data.data_file:
            with archive.m_context.raw_file(self.data_file) as file:
                sims_dict = parse_depthprofile_data(file)
                self.name = sims_dict["depth_profile_id"]
                self.Matrix = sims_dict["Matrix"]
                self.datetime = datetime.strptime(
                    sims_dict["date"], "%d.%m.%y"
                )  # noch in richtiges FOrmat ändern
                self.SampleID = sims_dict["sample_id"]
                self.lab_id = sims_dict["depth_profile_id"]
                logger.info("parser works")
                samples = CompositeSystemReference()
                samples.lab_id = sims_dict["sample_id"]
                samples.normalize(archive, logger)
                self.samples = [samples]
                results = MeasurementResults()
                results.depth_profiles_qualitative = []
                for count, value in enumerate(
                    sims_dict["depth_profiles_of_elements_qual"]
                ):
                    dep_profile_object = DepthProfileQualitative()
                    dep_profile_object.element = sims_dict[
                        "depth_profiles_of_elements_qual"
                    ][count]["element"]
                    dep_profile_object.depth = sims_dict[
                        "depth_profiles_of_elements_qual"
                    ][count]["depth"]
                    dep_profile_object.intensity = sims_dict[
                        "depth_profiles_of_elements_qual"
                    ][count]["intensity"]
                    results.depth_profiles_qualitative.append(dep_profile_object)
                results.depth_profiles_quantitative = []
                for count, value in enumerate(
                    sims_dict["depth_profiles_of_elements_quant"]
                ):
                    dep_profile_object = DepthProfileQuantitative()
                    dep_profile_object.element = sims_dict[
                        "depth_profiles_of_elements_quant"
                    ][count]["element"]
                    dep_profile_object.depth = sims_dict[
                        "depth_profiles_of_elements_quant"
                    ][count]["depth"]
                    dep_profile_object.atomic_concentration = sims_dict[
                        "depth_profiles_of_elements_quant"
                    ][count]["atomic_concentration"]
                    results.depth_profiles_quantitative.append(dep_profile_object)
                self.results = [results]
        super(RTGSIMSMeasurement, self).normalize(archive, logger)
        # should come here


m_package.__init_metainfo__()
