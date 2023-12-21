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
from datetime import datetime
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from nomad.units import ureg
from nomad.metainfo import (
    Quantity,
    Package,
    SubSection,
    MEnum,
    Section,)
from nomad.metainfo.metainfo import Category
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
    EntryDataCategory,)
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,)
from nomad.datamodel.metainfo.basesections import (
    Measurement,
    MeasurementResult,)

from nomad_measurements import (
    InSituMeasurement,
    ProcessReference)

m_package = Package(name='LayTec EpiTT Schema')

class IKZLayTecEpiTTCategory(EntryDataCategory):
    m_def = Category(label='IKZ LayTec EpiTT', categories=[EntryDataCategory])


class ReflectanceWavelengthTransient(ArchiveSection):
    m_def = Section(
        a_eln=dict(lane_width='600px'),
        label_quantity="wavelength",
        )
    wavelength = Quantity(
        type=np.dtype(np.int64),
        unit="nanometer",
        description='Reflectance Wavelength',
        )
    wavelength_name = Quantity(
        type=str,
        description='Name of Reflectance ',
        )
    intensity= Quantity(
        type=np.dtype(np.float64),
        shape = ['*'],
        )


class LayTecEpiTTMeasurementResult(ArchiveSection):
    '''
    Add description
    '''
    process_time = Quantity(
        type=np.dtype(np.float64),
        unit = "seconds",
        shape = ['*'],
        )
    pyrometer_temperature = Quantity(
        type=np.dtype(np.float64),
        description="PyroTemp transient. LayTec's TrueTemperature of the substrate surface --> Emissivity-corrected pyrometer ",
        unit = "celsius",
        shape = ['*'],
        )
    reflectance_wavelengths = SubSection(section_def=ReflectanceWavelengthTransient, repeats=True)


class MeasurementSettings(ArchiveSection):
    '''
    Add description
    '''
    module_name = Quantity(
        type=str, #'Ring TT1 1',
        description='MODULE_NAME',
        )
    wafer_label = Quantity(
        type=str, #'Al Zone 1 (Center)',
        description='WAFER_LABEL',
        )
    wafer_zone = Quantity(
        type=str, #'Center',
        description='WAFER_ZONE',
        )
    wafer = Quantity(
        type=str, #'1',
        description='WAFER',
        )
    runtype_ID = Quantity(
        type=str, #'20',
        description='RUNTYPE_ID',
        )
    runtype_name = Quantity(
        type=str, #'AlGa510mm90',
        description='RUNTYPE_NAME',
        )


class LayTecEpiTTMeasurement(InSituMeasurement, PlotSection, EntryData):
    '''
    LayTec's EpiTT is an emissivity-corrected pyrometer and
    reflectance measurement for in-situ measurement during
    growth processes (https://www.laytec.de/epitt)
    '''
    m_def = Section(
        a_eln={
            "lane_width": '600px',
            "hide": ['steps']
        },
        categories=[IKZLayTecEpiTTCategory],
        label='EpiTT Measurement',
        a_template=dict(
            instruments=[dict(name='LayTec_EpiTT', lab_id='LayTec_EpiTT_MOVPE_Ga2O3')],
        ),
    )
    method = Quantity(
        type=str,
        description='Method used to collect the data',
        default='LayTec_EpiTT'
    )
    location = Quantity(
        type=str,
        description='''
        The location of the process in longitude, latitude.
        ''',
        default='52.431685, 13.526855', #IKZ coordinates
    )
    data_file = Quantity(
        type=str,
        description='Data file containing the EpiTT data (*.dat)',
        a_eln=dict(
            component='FileEditQuantity',
        )
    )
    measurement_settings = SubSection(
        section_def=MeasurementSettings
    )
    results = SubSection(
        section_def=LayTecEpiTTMeasurementResult,
        #repeats=True,
    )

    def normalize(self, archive, logger):
        super(LayTecEpiTTMeasurement, self).normalize(archive, logger)
        logger.info('LayTecEpiTTMeasurement.normalize called')

        def parse_epitt_data(file):
            line = file.readline().strip()
            parameters = {}
            header = []
            while line.startswith(("##","!",)) or line.strip()=="":
                match = re.match(r"##(\w+)\s*=\s*(.*)", line.strip())
                if match:
                    parameter_name = match.group(1)
                    parameter_value = match.group(2)
                    if parameter_name == "YUNITS":
                        yunits = parameter_value.split("\t")
                        parameters[parameter_name] = yunits
                    else:
                        parameters[parameter_name] = parameter_value
                line = file.readline().strip()
            header=line.split("\t")
            data_in_df = pd.read_csv(file,sep="\t",names=header,skipfooter=1)
            return parameters, data_in_df

        if archive.data.data_file:
            with archive.m_context.raw_file(self.data_file) as file:
                epitt_data=parse_epitt_data(file)
                name_string=""
                paramters_for_name=["RUN_ID","RUNTYPE_ID","RUNTYPE_NAME","MODULE_NAME","WAFER_LABEL","WAFER"]
                for p in paramters_for_name:
                    if p in epitt_data[0].keys():
                        name_string += "_" + epitt_data[0][p]
                if name_string != "":
                    self.name = name_string[1:]
                    self.lab_id = name_string[1:]
                if "TIME" in epitt_data[0].keys():
                    self.datetime = datetime.strptime(epitt_data[0]["TIME"],'%Y-%m-%d-%H-%M-%S') #'2020-08-27-11-11-30',
                self.measurement_settings = MeasurementSettings() #?
                if "MODULE_NAME" in epitt_data[0].keys():
                    self.measurement_settings.module_name = epitt_data[0]["MODULE_NAME"]
                if "WAFER_LABEL" in epitt_data[0].keys():
                    self.measurement_settings.wafer_label = epitt_data[0]["WAFER_LABEL"]
                if "WAFER_ZONE" in epitt_data[0].keys():
                    self.measurement_settings.wafer_zone = epitt_data[0]["WAFER_ZONE"]
                if "WAFER" in epitt_data[0].keys():
                    self.measurement_settings.wafer = epitt_data[0]["WAFER"]
                #if "RUN_ID" in epitt_data[0].keys():
                #    self.run_ID = epitt_data[0]["RUN_ID"]
                if "RUNTYPE_ID" in epitt_data[0].keys():
                    self.measurement_settings.runtype_ID = epitt_data[0]["RUNTYPE_ID"]
                if "RUNTYPE_NAME" in epitt_data[0].keys():
                    self.measurement_settings.runtype_name = epitt_data[0]["RUNTYPE_NAME"]
                #self.time_transient = epitt_data[1]["BEGIN"]
                process = ProcessReference()
                process.lab_id=epitt_data[0]["RUN_ID"]
                process.normalize(archive, logger)
                self.process = process
                results = LayTecEpiTTMeasurementResult()
                results.process_time = epitt_data[1]["BEGIN"]
                results.pyrometer_temperature = epitt_data[1]["PyroTemp"]
                results.reflectance_wavelengths = []
                for wl, datacolname in zip(['REFLEC_WAVELENGTH', 'PYRO_WAVELENGTH', 'WHITE_WAVELENGTH'],["DetReflec", "RLo", "DetWhite"]):
                    if wl in epitt_data[0].keys():
                        transient_object = ReflectanceWavelengthTransient()
                        transient_object.wavelength = int(round(float(epitt_data[0][wl]))) #* ureg("nanometer") #float(epitt_data[0][wl])* ureg('nanometer')
                        transient_object.wavelength_name = wl #epitt_data[0]["REFLEC_WAVELENGTH"]
                        transient_object.intensity = epitt_data[1][datacolname]
                        results.reflectance_wavelengths.append(transient_object)
                self.results = [results]

        # plots
        temperature_figure = px.scatter(
            x=self.results[0].process_time,
            y=self.results[0].pyrometer_temperature,
            color=self.results[0].pyrometer_temperature,
            title="Temperature")
        temperature_figure.update_traces(mode='markers', marker={"size":3})
        temperature_figure.update_xaxes(title_text='Time [s]')
        temperature_figure.update_yaxes(title_text='Temperature [°C]')
        self.figures.append(PlotlyFigure(label='Temperature', index=1, figure=temperature_figure.to_plotly_json()))
        reflectance_figure = go.Figure()
        for i, _ in enumerate(self.results[0].reflectance_wavelengths):
            single_reflectance_figure =px.scatter(
                x=self.results[0].process_time.magnitude,
                y=self.results[0].reflectance_wavelengths[i].intensity,
                )
            single_reflectance_figure.update_traces(mode='lines+markers', line={'width': 1}, marker={"size":3})
            single_reflectance_figure.update_xaxes(title_text='Time [s]')
            single_reflectance_figure.update_yaxes(title_text='Reflectance')
            self.figures.append(PlotlyFigure(
                label=f"{self.results[0].reflectance_wavelengths[i].wavelength} nm",
                index=i + 2,
                figure=single_reflectance_figure.to_plotly_json()))
            reflectance_figure.add_trace(go.Scatter(
            x=self.results[0].process_time.magnitude,
            y=self.results[0].reflectance_wavelengths[i].intensity,
            name=f'{self.results[0].reflectance_wavelengths[i].wavelength} nm',
            mode='lines'
            ))
            reflectance_figure.update_traces(mode='lines+markers', line={'width': 1}, marker={"size":3})
            reflectance_figure.update_xaxes(title_text='Time [s]')
            reflectance_figure.update_yaxes(title_text='Reflectance')
        self.figures.append(PlotlyFigure(
            label='Reflectance',
            index=0,
            figure=reflectance_figure.to_plotly_json()))

m_package.__init_metainfo__()