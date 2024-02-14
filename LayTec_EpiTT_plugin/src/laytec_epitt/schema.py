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
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
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
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure

from nomad_measurements import (
    InSituMeasurement,
    ProcessReference,
)

m_package = Package(name="LayTec EpiTT Schema")


class IKZLayTecEpiTTCategory(EntryDataCategory):
    m_def = Category(label="IKZ LayTec EpiTT", categories=[EntryDataCategory])


class ReflectanceWavelengthTransient(PlotSection, ArchiveSection):
    m_def = Section(
        a_eln=dict(lane_width="600px"),
        label_quantity="wavelength",
    )
    wavelength = Quantity(
        type=np.dtype(np.float64),
        unit="nanometer",
        description="Reflectance Wavelength",
    )
    wavelength_name = Quantity(
        type=str,
        description="Name of Reflectance ",
    )
    raw_intensity = Quantity(
        type=np.dtype(np.float64),
        shape=["*"],
        description="Normalized reflectance wavelength",
    )
    autocorrelation_starting_point = Quantity(
        type=np.int64,
        a_eln={"component": "NumberEditQuantity"},
    )
    autocorrelation_period = Quantity(
        type=np.int64,
        a_eln={"component": "NumberEditQuantity"},
    )
    autocorrelated_intensity = Quantity(
        type=np.dtype(np.float64),
        shape=["*"],
    )


class LayTecEpiTTMeasurementResult(MeasurementResult):
    """
    Add description
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            lane_width="300px",
        ),
    )

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
        description="description",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Notes",
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
    process = SubSection(
        section_def=ProcessReference,
        description="A reference to the process during which the measurement occurred.",
        label="growth_process",
    )
    measurement_settings = SubSection(section_def=MeasurementSettings)
    results = SubSection(
        section_def=LayTecEpiTTMeasurementResult,
        # repeats=True,
    )

    def normalize(self, archive, logger):
        super(LayTecEpiTTMeasurement, self).normalize(archive, logger)
        logger.info("Executed LayTecEpiTTMeasurement normalizer.")

        # reference the growth process entry
        if self.process.name:
            self.process.normalize(archive, logger)
            logger.info("Executed LayTecEpiTTMeasurement.process normalizer.")
            if hasattr(self.process.reference, "grown_sample"):
                sample_list = []
                sample_list.append(
                    CompositeSystemReference(
                        lab_id=self.process.reference.grown_sample.lab_id,
                    ),
                )
                self.samples = sample_list
                self.samples[0].normalize(archive, logger)
            else:
                logger.warning(
                    "No grown_sample found in GrowthMovpe2.grown_sample. "
                    + "No sample is referenced in LayTecEpiTTMeasurement. "
                    + "Please upload a growth process file and reprocess."
                )

        # noise smoothening with autocorrelated function
        for trace in self.results[0].reflectance_wavelengths:
            if not getattr(trace, "autocorrelation_starting_point"):
                setattr(trace, "autocorrelation_starting_point", 0)
            if not getattr(trace, "autocorrelation_period"):
                setattr(trace, "autocorrelation_period", len(trace.raw_intensity))
            start = trace.autocorrelation_starting_point
            period = trace.autocorrelation_period
            if period is not None and start is not None:
                trace.autocorrelated_intensity = (
                    pd.Series(trace.raw_intensity[start : (start + period)])
                    .rolling(30)
                    .mean()
                )

        # plots
        if self.results[0]:
            overview_fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=["Reflectance"],
            )

            temperature_object = go.Scattergl(
                x=self.results[0].process_time,
                y=self.results[0].pyrometer_temperature,
                # color=self.results[0].pyrometer_temperature,
                mode="lines+markers",
                line={"width": 2},
                marker={"size": 2},
                showlegend=False,
            )
            overview_fig.add_trace(temperature_object, row=2, col=1)
            for trace in self.results[0].reflectance_wavelengths:
                trace_min = trace.autocorrelation_starting_point
                trace_max = (
                    trace.autocorrelation_starting_point + trace.autocorrelation_period
                )
                single_trace_fig = make_subplots(
                    rows=2,
                    cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    subplot_titles=["Reflectance"],
                )
                go_object = go.Scattergl(
                    x=self.results[0].process_time,
                    y=trace.raw_intensity,
                    mode="lines+markers",
                    line={"width": 2},
                    marker={"size": 2},
                    # marker=dict(
                    #     color=np.log10(self.results[0].intensity),
                    #     colorscale="inferno",
                    #     line_width=0,
                    #     showscale=True,
                    # ),
                    name=f"{trace.wavelength.magnitude} nm",
                )
                x_slice = self.results[0].process_time[trace_min:trace_max]
                y_slice = trace.raw_intensity[trace_min:trace_max]
                single_trace_fig.add_trace(
                    go_object,  # go_object,
                    row=1,
                    col=1,
                )
                overview_fig.add_trace(
                    go_object,
                    row=1,
                    col=1,
                )
                if (
                    trace.autocorrelated_intensity is not None
                    and trace.autocorrelated_intensity.any()
                ):
                    x_slice = self.results[0].process_time[trace_min:trace_max]
                    y_slice = trace.autocorrelated_intensity[1:]
                    go_object = go.Scattergl(
                        x=x_slice,
                        y=y_slice,
                        mode="lines+markers",
                        line={"width": 2},
                        marker={"size": 2},
                        name=f"Autocorr. {trace.wavelength.magnitude} nm",
                    )
                    single_trace_fig.add_trace(
                        go_object,
                        row=2,
                        col=1,
                    )
                single_trace_fig.update_layout(
                    height=800,
                    # width=1000,
                    showlegend=False,
                    dragmode="pan",
                )
                single_trace_fig.update_xaxes(
                    title_text="",
                    autorange=False,
                    range=[trace_min, trace_max],
                    fixedrange=False,
                    ticks="",  # "outside",
                    showticklabels=False,
                    showline=True,
                    linewidth=1,
                    linecolor="black",
                    mirror=True,
                    row=1,
                    col=1,
                )
                single_trace_fig.update_xaxes(
                    title_text="Time [s]",
                    autorange=False,
                    range=[trace_min, trace_max],
                    fixedrange=False,
                    ticks="",  # "outside",
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor="black",
                    mirror=True,
                    row=2,
                    col=1,
                )
                single_trace_fig.update_yaxes(
                    title_text="Intensity [a. u.]",
                    fixedrange=False,
                    ticks="",  # "outside",
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor="black",
                    mirror=True,
                    row=1,
                    col=1,
                )
                single_trace_fig.update_yaxes(
                    title_text="Autocorrelated Int. [a. u.]",
                    fixedrange=False,
                    ticks="",  # "outside",
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor="black",
                    mirror=True,
                    row=2,
                    col=1,
                )
                single_trace_fig_json = single_trace_fig.to_plotly_json()
                single_trace_fig_json["config"] = {
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "responsive": False,
                    "displaylogo": False,
                }
                trace.figures = [
                    PlotlyFigure(
                        label=f"{trace.wavelength.magnitude} nm",
                        index=1,
                        figure=single_trace_fig_json,
                    )
                ]
            overview_fig.update_layout(
                height=800,
                # width=800,
                showlegend=True,
                legend=dict(
                    orientation="h",  # "h",
                    bgcolor="rgba(0,0,0,0)",
                    # yanchor="bottom",
                    # y=1.02,
                    # xanchor="center",
                    # x=1,
                    yanchor="bottom",
                    y=0.51,
                    xanchor="left",
                    x=0.01,
                    itemwidth=30,
                ),
            )
            overview_fig.update_yaxes(
                title_text="Intensity [a.u.]",
                fixedrange=True,
                ticks="",  # "outside",
                showticklabels=True,
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                row=1,
                col=1,
            )
            overview_fig.update_yaxes(
                title_text="Temperature [°C]",
                fixedrange=True,
                ticks="",  # "outside",
                showticklabels=True,
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                row=2,
                col=1,
            )
            overview_fig.update_xaxes(
                title_text="",
                # autorange=False,
                # range=[trace_min, trace_max],
                fixedrange=True,
                ticks="",  # "outside",
                showticklabels=False,
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                row=1,
                col=1,
            )
            overview_fig.update_xaxes(
                title_text="Time [s]",
                # autorange=False,
                # range=[trace_min, trace_max],
                fixedrange=True,
                ticks="",  # "outside",
                showticklabels=True,
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                row=2,
                col=1,
            )
            overview_fig_json = overview_fig.to_plotly_json()
            overview_fig_json["config"] = {
                "scrollZoom": False,
                "responsive": False,
                "displaylogo": False,
                "staticPlot": True,
                "dragmode": False,
            }
            self.figures = [PlotlyFigure(label="figure 1", figure=overview_fig_json)]

m_package.__init_metainfo__()
