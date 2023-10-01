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
import os

from baseclasses.solar_energy import (
    PLMeasurement,
    UVvisMeasurementLibrary, UVvisDataSimple, UVvisSingleLibraryMeasurement, UVvisProperties,
    ConductivityMeasurementLibrary, ConductivitySingleLibraryMeasurement  # , UVvisProperties
)
from baseclasses.characterizations import (
    XRFLibrary, XRFSingleLibraryMeasurement, XRFProperties, XRFComposition, XRFData)
from baseclasses.helper.utilities import convert_datetime
from baseclasses import (
    LibrarySample
)
from nomad.datamodel.data import EntryData
import datetime

from nomad_material_processing.physical_vapor_deposition import (
    PVDChamberEnvironment,
    PVDMaterialEvaporationRate,
    PVDMaterialSource,
    PVDPressure,
    PVDSourcePower,
    PVDSubstrate,
    PVDSubstrateTemperature,
    ThermalEvaporation,
    ThermalEvaporationHeater,
    ThermalEvaporationHeaterTemperature,
    ThermalEvaporationSource,
    ThermalEvaporationStep,
)
from nomad_material_processing.utils import create_archive
from structlog.stdlib import (
    BoundLogger,
)
from nomad.metainfo import (
    Package,
    Section,
    Quantity,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    BrowserAnnotation,
)
from nomad.datamodel.metainfo.eln import (
    Substance,
)
from nomad.metainfo.metainfo import (
    Category,
)
from nomad.datamodel.data import (
    EntryDataCategory,
)

m_package = Package(name='HZB Unold Lab')

substance_translation = {
    'PbI2': 'Lead Iodide',
    'CsI': 'Cesium Iodide',
    'PbBr2': 'Lead Bromide',
    'CsBr': 'Cesium Bromide'
}


class HZBUnoldLabCategory(EntryDataCategory):
    m_def = Category(label='HZB Unold Lab', categories=[EntryDataCategory])


class HZBUnoldLibrary(LibrarySample, EntryData):
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        a_eln=dict(
            hide=["users", "elemental_composition", "components"]))

    qr_code = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    def normalize(self, archive, logger):
        super(HZBUnoldLibrary,
              self).normalize(archive, logger)

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if self.lab_id:
            import qrcode
            from PIL import ImageDraw, ImageFont
            msg = f'{self.lab_id}#'
            img = qrcode.make(msg)
            Im = ImageDraw.Draw(img)
            fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeSans.ttf", 13)

            # Add Text to an image
            Im.text((15, 15), f"{self.lab_id}", font=fnt)
            qr_file_name = f"{self.lab_id}.png"
            img.save(os.path.join(path, qr_file_name), dpi=(2000, 2000))
            self.qr_code = qr_file_name


class HZBUnoldXRFLibrary(XRFLibrary, EntryData):
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        a_eln=dict(hide=['instruments', 'steps', 'results', 'lab_id'],
                   properties=dict(
            order=[
                "name",
            ])),
        a_plot=[
            {
                'x': 'energy', 'y': 'measurements/:/data/intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                            "scrollZoom": True, 'staticPlot': False, }}]
    )

    def normalize(self, archive, logger):

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if self.samples and self.samples[0].lab_id:
            search_folder = self.samples[0].lab_id

            for item in os.listdir(path):
                if not os.path.isdir(os.path.join(path, item)):
                    continue
                if item != search_folder:
                    continue
                self.data_folder = item

        if self.data_folder is not None and self.composition_file is not None:
            measurements = []

            data_folder = os.path.join(path, self.data_folder)

            from baseclasses.helper.file_parser.xrf_spx_parser import read as xrf_read
            import pandas as pd
            files = [os.path.join(data_folder, file) for file in os.listdir(data_folder) if file.endswith(".spx")]
            files.sort()

            spectra, energy, measurement_rows, positions_array, position_axes, (len_x, len_y, order_letter) = xrf_read(
                files)
            self.datetime = convert_datetime(
                measurement_rows[0]["DateTime"], datetime_format="%Y-%m-%dT%H:%M:%S.%f", utc=False)
            self.energy = energy
            composition_data = pd.read_excel(os.path.join(path, self.composition_file))
            for i, spectrum in enumerate(spectra):

                data = XRFData(intensity=spectrum)
                composition = [XRFComposition(name=col, amount=composition_data[col].iloc[i])
                               for col in composition_data.columns[1:]]
                measurements.append(XRFSingleLibraryMeasurement(
                    data_file=os.path.basename(os.path.join(self.data_folder, files[i])),
                    position_x=position_axes[0][i % len_x],  # positions_array[0, i],
                    position_y=position_axes[1][i // len_x],  # positions_array[1, i],
                    # position_index=i,
                    # position_x_relative=position_axes[0][i % len_x],
                    # position_y_relative=position_axes[1][i // len_x],
                    thickness=composition_data[composition_data.columns[0]].iloc[i],
                    data=data,
                    composition=composition,
                    name=f"{position_axes[0][i % len_x]},{position_axes[1][i // len_x]}"),
                )
            self.measurements = measurements
        super(HZBUnoldXRFLibrary,
              self).normalize(archive, logger)


class HZBUnoldUVvisReflectionLibrary(UVvisMeasurementLibrary, EntryData):
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        a_eln=dict(hide=['instruments', 'steps', 'results', 'lab_id'],
                   properties=dict(
            order=[
                "name",
            ])),
        a_plot=[
            {
                'x': 'wavelength', 'y': 'measurements/:/data/intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                            "scrollZoom": True, 'staticPlot': False, }}]
    )

    def normalize(self, archive, logger):

        spec_key = "reflection_spec.csv"
        reference_key = "reflection_reference.csv"
        prefix = 'refl'
        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if not self.reference_file:

            for file in os.listdir(path):
                if not file.endswith(reference_key):
                    continue
                self.reference_file = file

        if self.data_file and self.reference_file:
            measurements = []

            from baseclasses.helper.file_parser.uvvis_parser import read_uvvis
            reflectance, wavelength, x_pos, y_pos, md = read_uvvis(
                [os.path.join(path, file) for file in [self.data_file, self.reference_file]], spec_key, reference_key, prefix)

            if self.properties is None:
                self.properties = UVvisProperties(integration_time=md['integration_time'].split("s")[0].strip(),
                                                  number_of_averages=md['no. averages'])

            self.wavelength = wavelength
            for ix in range(len(x_pos)):
                for iy in range(len(y_pos)):

                    data = UVvisDataSimple(intensity=reflectance[ix, iy, :])

                    measurements.append(UVvisSingleLibraryMeasurement(
                        position_x=x_pos[ix],
                        position_y=y_pos[iy],
                        data=data,
                        name=f"{x_pos[ix]},{y_pos[iy]}"),
                    )
            self.measurements = measurements
        super(HZBUnoldUVvisReflectionLibrary,
              self).normalize(archive, logger)


class HZBUnoldUVvisTransmissionLibrary(UVvisMeasurementLibrary, EntryData):
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        a_eln=dict(hide=['instruments', 'steps', 'results', 'lab_id'],
                   properties=dict(
            order=[
                "name",
            ])),
        a_plot=[
            {
                'x': 'wavelength', 'y': 'measurements/:/data/intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                            "scrollZoom": True, 'staticPlot': False, }}]
    )

    def normalize(self, archive, logger):

        spec_key = "transmission_spec.csv"
        reference_key = "transmission_reference.csv"
        prefix = 'trans'

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if not self.reference_file:

            for file in os.listdir(path):
                if not file.endswith(reference_key):
                    continue
                self.reference_file = file

        if self.data_file and self.reference_file:
            measurements = []

            from baseclasses.helper.file_parser.uvvis_parser import read_uvvis
            transmission, wavelength, x_pos, y_pos, md = read_uvvis(
                [os.path.join(path, file) for file in [self.data_file, self.reference_file]], spec_key, reference_key, prefix)

            # self.datetime = convert_datetime(os.path.getctime(os.path.join(
            #     path, self.data_file)), utc=False, seconds=True)

            if self.properties is None:
                self.properties = UVvisProperties(integration_time=md['integration_time'].split("s")[0].strip(),
                                                  number_of_averages=md['no. averages'])

            self.wavelength = wavelength
            for ix in range(len(x_pos)):
                for iy in range(len(y_pos)):

                    data = UVvisDataSimple(intensity=transmission[ix, iy, :])

                    measurements.append(UVvisSingleLibraryMeasurement(
                        position_x=x_pos[ix],
                        position_y=y_pos[iy],
                        data=data,
                        name=f"{x_pos[ix]},{y_pos[iy]}"),
                    )
            self.measurements = measurements
        super(HZBUnoldUVvisTransmissionLibrary,
              self).normalize(archive, logger)


class HZBUnoldPLLibrary(UVvisMeasurementLibrary, EntryData):
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        a_eln=dict(hide=['instruments', 'steps', 'results', 'lab_id'],
                   properties=dict(
            order=[
                "name",
            ])),
        a_plot=[
            {
                'x': 'wavelength', 'y': 'measurements/:/data/intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                            "scrollZoom": True, 'staticPlot': False, }}]
    )

    def normalize(self, archive, logger):

        # spec_key = "transmission_spec.csv"
        # reference_key = "transmission_reference.csv"
        # prefix = 'trans'

        # with archive.m_context.raw_file(archive.metadata.mainfile) as f:
        #     path = os.path.dirname(f.name)

        # if not self.reference_file:

        #     for file in os.listdir(path):
        #         if not file.endswith(reference_key):
        #             continue
        #         self.reference_file = file

        # if self.data_file and self.reference_file:
        #     measurements = []

        #     from baseclasses.helper.file_parser.uvvis_parser import read_uvvis
        #     transmission, wavelength, x_pos, y_pos, md = read_uvvis(
        #         [os.path.join(path, file) for file in [self.data_file, self.reference_file]], spec_key, reference_key, prefix)

        #     if self.properties is None:
        #         self.properties = UVvisProperties(integration_time=md['integration_time'].split("s")[0].strip(),
        #                                           number_of_averages=md['no. averages'])

        #     self.wavelength = wavelength
        #     for ix in range(len(x_pos)):
        #         for iy in range(len(y_pos)):

        #             data = UVvisDataSimple(intensity=transmission[ix, iy, :])

        #             measurements.append(UVvisSingleLibraryMeasurement(
        #                 position_x=x_pos[ix],
        #                 position_y=y_pos[iy],
        #                 data=data,
        #                 name=f"{x_pos[ix]},{y_pos[iy]}"),
        #             )
        #     self.measurements = measurements
        super(HZBUnoldPLLibrary,
              self).normalize(archive, logger)


class HZBUnoldConductivityLibrary(ConductivityMeasurementLibrary, EntryData):
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        a_eln=dict(hide=['instruments', 'steps', 'results', 'lab_id'],
                   properties=dict(
            order=[
                "name",
            ])),
    )

    def normalize(self, archive, logger):

        with archive.m_context.raw_file(archive.metadata.mainfile) as f:
            path = os.path.dirname(f.name)

        if self.data_file:
            measurements = []

            from baseclasses.helper.file_parser.conductivity_parser import read_conductivity
            conductivity, x_pos, y_pos, md = read_conductivity(os.path.join(path, self.data_file))
            self.datetime = convert_datetime(md.loc["Date:"][1], datetime_format="%Y-%m-%d %H:%M:%S", utc=False)
            for ix in range(len(x_pos)):
                for iy in range(len(y_pos)):

                    measurements.append(ConductivitySingleLibraryMeasurement(
                        position_x=x_pos[ix],
                        position_y=y_pos[iy],
                        conductivity=conductivity[ix, iy],
                        name=f"{x_pos[ix]},{y_pos[iy]}"),
                    )
            self.measurements = measurements
        super(HZBUnoldConductivityLibrary,
              self).normalize(archive, logger)


class HZBUnoldLabSubstance(Substance, EntryData):
    pass


class HZBUnoldLabThermalEvaporation(ThermalEvaporation, EntryData):
    '''
    Class autogenerated from yaml schema.
    '''
    m_def = Section(
        categories=[HZBUnoldLabCategory],
        label='Thermal Evaporation Process',
        links=["http://purl.obolibrary.org/obo/CHMO_0001360"],
        a_plot=[
            dict(
                x='steps/:/sources/:/material_source/rate/process_time',
                y='steps/:/sources/:/material_source/rate/rate',
            ),
            dict(
                x='steps/:/sources/:/evaporation_source/temperature/process_time',
                y='steps/:/sources/:/evaporation_source/temperature/temperature',
            ),
            dict(
                x='steps/:/environment/pressure/process_time',
                y='steps/:/environment/pressure/pressure',
                layout=dict(
                    yaxis=dict(
                        type='log',
                    ),
                ),
            ),
        ],
    )
    log_file = Quantity(
        type=str,
        description='''
        The log file generated by the PVD software.
        ''',
        a_browser=BrowserAnnotation(
            adaptor='RawFileAdaptor'
        ),
        a_eln=ELNAnnotation(
            component='FileEditQuantity'
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `HZBUnoldLabThermalEvaporation` class. Will generate and
        fill the `steps` attribute using the `log_file`.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        if self.log_file:
            import pandas as pd
            import numpy as np
            with archive.m_context.raw_file(self.log_file, 'r') as fh:
                line = fh.readline().strip()
                metadata = {}
                while line.startswith('#'):
                    if ':' in line:
                        key = line.split(':')[0][1:].strip()
                        value = str.join(':', line.split(':')[1:]).strip()
                        metadata[key] = value
                    line = fh.readline().strip()
                df = pd.read_csv(fh, sep='\t')
            self.datetime = datetime.datetime.strptime(
                f'{metadata["Date"]}T{df["Time"].values[0]}',
                r'%Y/%m/%dT%H:%M:%S',
            )
            self.end_time = datetime.datetime.strptime(
                f'{metadata["Date"]}T{df["Time"].values[-1]}',
                r'%Y/%m/%dT%H:%M:%S',
            )
            self.name = f'PVD-{metadata["process ID"]}'
            self.location = 'Berlin, Germany'
            self.lab_id = f'HZB_{metadata["operator"]}_{self.datetime.strftime(r"%Y%m%d")}_PVD-{metadata["process ID"]}'

            source_materials = {column[0]: column.split()[2] for column in df.columns if column[-1:] == 'T'}

            qcms = ['QCM1_1', 'QCM1_2', 'QCM2_1', 'QCM2_2']
            qcms_source_number = {df[qcm[:-2]+" FILMNAM"+qcm[-2:]].values[0]: qcm for qcm in qcms}
            try:
                qcms_ordered = [qcms_source_number[int(source)] for source in source_materials]
            except KeyError:
                raise ValueError("Film names do not match source names.")
            shutters = [f'{qcm[:-2]} SHTSRC{qcm[-2:]}' for qcm in qcms_ordered]
            start_times = []
            for shutter in shutters:
                switch_times = df.loc[df[shutter].diff() != 0, 'Process Time in seconds'].values
                for time in switch_times:
                    if not any(abs(t - time) < 5 for t in start_times):
                        start_times.append(time)
            start_times.append(df.iloc[-1, 1])
            substances = {
                source_nr: create_archive(
                    entity=HZBUnoldLabSubstance(
                        name=substance_translation.get(
                            source_materials[source_nr],
                            source_materials[source_nr]
                        ),
                    ),
                    archive=archive,
                    file_name=f'{source_materials[source_nr]}_substance.archive.json',
                ) for source_nr in source_materials
            }
            steps = []
            depositions = 0
            for idx, time in enumerate(start_times[:-1]):
                step = df.loc[
                    (time <= df['Process Time in seconds'])
                    & (df['Process Time in seconds'] < start_times[idx + 1])
                ]
                if step.loc[:, shutters].mode().any().any():
                    depositions += 1
                    name = f'deposition {depositions}'
                elif idx == 0:
                    name = 'pre'
                else:
                    name = 'post'
                sources = []
                for source_nr in source_materials:
                    source = f'{source_nr} - {source_materials[source_nr]}'
                    material_source = PVDMaterialSource(
                        material=substances[source_nr],
                        rate=PVDMaterialEvaporationRate(
                            rate=1e-6 * step[f'{source} PV'],
                            process_time=step['Process Time in seconds'],
                            measurement_type='Quartz Crystal Microbalance',
                        ),
                    )
                    evaporation_source = ThermalEvaporationHeater(
                        temperature=ThermalEvaporationHeaterTemperature(
                            temperature=step[f'{source} T'] + 273.15,
                            process_time=step['Process Time in seconds'],
                        ),
                        power=PVDSourcePower(
                            power=step[f'{source} Aout'],
                            process_time=step['Process Time in seconds']
                        ),
                    )
                    thermal_evaporation_source = ThermalEvaporationSource(
                        name=source_materials[source_nr],
                        material_source=material_source,
                        evaporation_source=evaporation_source,
                    )
                    sources.append(thermal_evaporation_source)
                substrate = PVDSubstrate(
                    substrate=None,  # TODO: Add substrate
                    temperature=PVDSubstrateTemperature(
                        temperature=step['Substrate PV'] + 273.15,
                        process_time=step['Process Time in seconds'],
                        measurement_type='Heater thermocouple',
                    ),
                    heater='Resistive element',
                    distance_to_source=[
                        np.linalg.norm(np.array((41.54e-3, 26.06e-3, 201.12e-3)))
                    ] * 4,
                )
                environment = PVDChamberEnvironment(
                    pressure=PVDPressure(
                        pressure=step['Vacuum Pressure2'] * 1e2,
                        process_time=step['Process Time in seconds'],
                    ),
                )
                step = ThermalEvaporationStep(
                    name=name,
                    creates_new_thin_film=step.loc[:, shutters].mode().any().any(),
                    duration=start_times[idx + 1] - time,
                    sources=sources,
                    substrate=[substrate],
                    environment=environment,
                )
                steps.append(step)
            self.steps = steps

        super(HZBUnoldLabThermalEvaporation, self).normalize(archive, logger)


m_package.__init_metainfo__()
