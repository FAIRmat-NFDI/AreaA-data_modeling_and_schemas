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
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

from nomad.metainfo import (
    Quantity,
    Package,
    SubSection,
    Section,
)
from nomad.metainfo.metainfo import Category
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
    EntryDataCategory,
)
from nomad.datamodel.metainfo.basesections import (
    MeasurementResult,
    CompositeSystemReference,
)
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from nomad_measurements import InSituMeasurement

m_package = Package(name="LayTec EpiTT Schema")


class IKZLayTecEpiTTCategory(EntryDataCategory):
    m_def = Category(label="IKZ LayTec EpiTT", categories=[EntryDataCategory])


class ReflectanceWavelengthTransient(ArchiveSection):
    m_def = Section(
        a_eln=dict(lane_width="600px"),
        label_quantity="wavelength",
    )
    wavelength = Quantity(
        type=np.dtype(np.int64),
        unit="nanometer",
        description="Reflectance Wavelength",
    )
    wavelength_name = Quantity(
        type=str,
        description="Name of Reflectance ",
    )
    intensity = Quantity(
        type=np.dtype(np.float64),
        shape=["*"],
    )


class LayTecEpiTTMeasurementResult(MeasurementResult):
    """
    Add description
    """

    process_time = Quantity(
        type=np.dtype(np.float64),
        unit="seconds",
        shape=["*"],
    )
    pyrometer_temperature = Quantity(
        type=np.dtype(np.float64),
        description="PyroTemp transient. LayTec's TrueTemperature of the substrate surface --> Emissivity-corrected pyrometer ",
        unit="celsius",
        shape=["*"],
    )
    reflectance_wavelengths = SubSection(
        section_def=ReflectanceWavelengthTransient, repeats=True
    )


class MeasurementSettings(ArchiveSection):
    """
    Add description
    """

    module_name = Quantity(
        type=str,  #'Ring TT1 1',
        description="MODULE_NAME",
    )
    wafer_label = Quantity(
        type=str,  #'Al Zone 1 (Center)',
        description="WAFER_LABEL",
    )
    wafer_zone = Quantity(
        type=str,  #'Center',
        description="WAFER_ZONE",
    )
    wafer = Quantity(
        type=str,  #'1',
        description="WAFER",
    )
    runtype_ID = Quantity(
        type=str,  #'20',
        description="RUNTYPE_ID",
    )
    runtype_name = Quantity(
        type=str,  #'AlGa510mm90',
        description="RUNTYPE_NAME",
    )


class LayTecEpiTTMeasurement(InSituMeasurement, PlotSection, EntryData):
    """
    LayTec's EpiTT is an emissivity-corrected pyrometer and
    reflectance measurement for in-situ measurement during
    growth processes (https://www.laytec.de/epitt)
    """

    m_def = Section(
        a_eln={"lane_width": "600px", "hide": ["steps"]},
        categories=[IKZLayTecEpiTTCategory],
        label="EpiTT Measurement",
        a_template=dict(
            instruments=[dict(name="LayTec_EpiTT", lab_id="LayTec_EpiTT_MOVPE_Ga2O3")],
        ),
    )
    description = Quantity(
        type=str,
        description="""
        Notes and description of the current entry.
        """,
        a_eln=dict(
            component="StringEditQuantity",
        ),
    )
    method = Quantity(
        type=str, description="Method used to collect the data", default="LayTec_EpiTT"
    )
    location = Quantity(
        type=str,
        description="""
        The location of the process in longitude, latitude.
        """,
        default="52.431685, 13.526855",  # IKZ coordinates
    )
    data_file = Quantity(
        type=str,
        description="Data file containing the EpiTT data (*.dat)",
        a_eln=dict(
            component="FileEditQuantity",
        ),
    )
    measurement_settings = SubSection(section_def=MeasurementSettings)
    results = SubSection(
        section_def=LayTecEpiTTMeasurementResult,
        # repeats=True,
    )

    def normalize(self, archive, logger):
        super(LayTecEpiTTMeasurement, self).normalize(archive, logger)
        logger.info("Executed LayTecEpiTTMeasurement normalizer.")

        # reference process
        if self.process.name:
            self.process.normalize(archive, logger)
            logger.info("Executed LayTecEpiTTMeasurement.process normalizer.")
            if self.process.reference.grown_sample.lab_id:
                sample_list = []
                sample_list.append(
                    CompositeSystemReference(
                        lab_id=self.process.reference.grown_sample.lab_id,
                    ),
                )
                self.samples = sample_list
                self.samples[0].normalize(archive, logger)
            else:
                logger.error(
                    "No lab_id found in GrowthMovpe2.grown_sample.lab_id.\
                     No sample is referenced in LayTecEpiTTMeasurement."
                )

        # plots
        if self.results[0]:
            figures_list = []
            temperature_figure = px.scatter(
                x=self.results[0].process_time,
                y=self.results[0].pyrometer_temperature,
                color=self.results[0].pyrometer_temperature,
                title="Temperature",
            )
            temperature_figure.update_traces(mode="markers", marker={"size": 3})
            temperature_figure.update_xaxes(title_text="Time [s]")
            temperature_figure.update_yaxes(title_text="Temperature [°C]")
            figures_list.append(
                PlotlyFigure(
                    label="Temperature",
                    index=1,
                    figure=temperature_figure.to_plotly_json(),
                )
            )
            reflectance_figure = go.Figure()
            for i, _ in enumerate(self.results[0].reflectance_wavelengths):
                single_reflectance_figure = px.scatter(
                    x=self.results[0].process_time.magnitude,
                    y=self.results[0].reflectance_wavelengths[i].intensity,
                )
                single_reflectance_figure.update_traces(
                    mode="lines+markers", line={"width": 1}, marker={"size": 3}
                )
                single_reflectance_figure.update_xaxes(title_text="Time [s]")
                single_reflectance_figure.update_yaxes(title_text="Reflectance")
                figures_list.append(
                    PlotlyFigure(
                        label=f"{self.results[0].reflectance_wavelengths[i].wavelength} nm",
                        index=i + 2,
                        figure=single_reflectance_figure.to_plotly_json(),
                    )
                )
                reflectance_figure.add_trace(
                    go.Scatter(
                        x=self.results[0].process_time.magnitude,
                        y=self.results[0].reflectance_wavelengths[i].intensity,
                        name=f"{self.results[0].reflectance_wavelengths[i].wavelength} nm",
                        mode="lines",
                    )
                )
                reflectance_figure.update_traces(
                    mode="lines+markers", line={"width": 1}, marker={"size": 3}
                )
                reflectance_figure.update_xaxes(title_text="Time [s]")
                reflectance_figure.update_yaxes(title_text="Reflectance")
            figures_list.append(
                PlotlyFigure(
                    label="Reflectance",
                    index=0,
                    figure=reflectance_figure.to_plotly_json(),
                )
            )
            self.figures = figures_list


#            if self.process.reference:
# with archive.m_context.raw_file(self.process.reference, 'r') as process_file:
#     process_dict = yaml.safe_load(process_file)
#     updated_dep_control['data']['grown_sample'] = GrownSamples(
#             reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, sample_filename)}#data",
#         ).m_to_dict()

m_package.__init_metainfo__()
