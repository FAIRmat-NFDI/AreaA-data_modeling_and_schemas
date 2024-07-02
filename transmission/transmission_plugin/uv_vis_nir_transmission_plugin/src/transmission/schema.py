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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Union,
)

import numpy as np
import plotly.express as px
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    PureSubstanceComponent,
    PubChemPureSubstanceSection,
    Instrument,
    InstrumentReference,
    Measurement,
    MeasurementResult,
    ReadableIdentifiers,
    Entity,
)
import numpy as np
import plotly.express as px
from nomad.metainfo import (
    MEnum,
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad.units import ureg

from transmission.readers import read_asc
from transmission.utils import create_archive, merge_sections

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger


m_package = Package(name='nomad_transmission')


class TransmissionSpectrophotometer(Instrument, EntryData):
    """
    Entry section for the transmission spectrophotometer.
    """

    m_def = Section()
    serial_number = Quantity(
        type=str,
        description='Instrument serial number.',
        a_eln={'component': 'StringEditQuantity'},
    )
    software_version = Quantity(
        type=str,
        description='Software/firmware version.',
        a_eln={'component': 'StringEditQuantity'},
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `TransmissionSpectrophotometer` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class TransmissionSample(Entity, EntryData):
    """
    Entry section for the sample used in the transmission measurement. Contains the
    physical properties of the sample, and the information about the material system.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'length',
                    'orientation',
                    'description',
                ]
            )
        )
    )
    length = Quantity(
        type=np.float64,
        description=(
            'Length (or thickness) of the sample. '
            'The dimension of the sample along the path of the light beam.'
        ),
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'mm',
        },
        unit='mm',
    )
    orientation = Quantity(
        type=str,
        description='Crystallographic orientation of the sample.',
        a_eln={'component': 'StringEditQuantity'},
    )
    material_system = SubSection(
        section_def=CompositeSystem,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `TransmissionSample` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)


class Accessory(ArchiveSection):
    """
    Section for adding setting for a custom accessory.
    """

    m_def = Section(
        description='An accessory used in the instrument.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'description',
                ],
            ),
        ),
    )
    name = Quantity(
        type=str,
        description='Name of the accessory.',
        a_eln={'component': 'StringEditQuantity'},
    )
    description = Quantity(
        type=str,
        description='Description of the accessory.',
        a_eln={'component': 'RichTextEditQuantity'},
    )


class PolDepol(Accessory):
    """
    Optional accessory to polarize or depolarize the light beam entering the sample.
    """

    m_def = Section(
        description=(
            'Optional accessory to polarize or depolarize the light beam '
            'entering the sample.'
        ),
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'mode',
                    'polarizer_angle',
                ],
            ),
        ),
    )

    mode = Quantity(
        type=MEnum(['Polarizer', 'Depolarizer']),
        description='Mode of the accessory: either polarizer or depolarizer.',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )
    polarizer_angle = Quantity(
        type=np.float64,
        description='Value of polarization angle when polarizer mode is used.',
        a_eln={'component': 'NumberEditQuantity'},
        unit='degrees',
    )

    def normalize(self, archive, logger):
        if self.mode is None or self.mode == 'Depolarizer':
            if self.polarizer_angle is not None:
                logger.warning(
                    'Ambiguous polarizer angle: '
                    'PolDepol accessory is not set to "Polarizer" mode, '
                    'but `polarizer_angle` is set.'
                )
        super().normalize(archive, logger)


class Aperture(Accessory):
    """
    Section for adding settings of a custom aperture.
    """

    m_def = Section(
        description="""
        Custom aperture placed in front of the sample inside the sample compartment.
        """,
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'diameter',
                ],
            ),
        ),
    )
    diameter = Quantity(
        type=np.float64,
        description='Diameter of the aperture.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'mm',
        },
        unit='mm',
    )


class SettingOverWavelengthRange(ArchiveSection):
    """
    An instrument setting set over a range of wavelength.
    """

    m_def = Section(
        description='An instrument setting set over a range of wavelength.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'wavelength_upper_limit',
                    'wavelength_lower_limit',
                    'value',
                ],
            ),
        ),
    )
    name = Quantity(
        type=str,
        description='Short description containing wavelength range.',
        a_eln={'component': 'StringEditQuantity'},
    )
    wavelength_upper_limit = Quantity(
        type=np.float64,
        description='Upper limit of wavelength range.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
    )
    wavelength_lower_limit = Quantity(
        type=np.float64,
        description='Lower limit of wavelength range.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
    )
    value = Quantity(
        type=np.float64,
        description='Value of the given instrument setting.',
        a_eln={'component': 'NumberEditQuantity'},
        unit='dimensionless',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `SettingOverWavelengthRange` class.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)

        upper_limit = '-'
        lower_limit = '-'
        if self.wavelength_upper_limit is not None:
            upper_limit = self.wavelength_upper_limit.magnitude
        if self.wavelength_lower_limit is not None:
            lower_limit = self.wavelength_lower_limit.magnitude
        if isinstance(upper_limit, float) and isinstance(lower_limit, float):
            if upper_limit < lower_limit:
                logger.warning(
                    f'Upper limit of wavelength "{upper_limit}" should be greater than'
                    f'lower limit of wavelength "{lower_limit}".'
                )
                upper_limit = '-'
                lower_limit = '-'
                self.wavelength_upper_limit = None
                self.wavelength_lower_limit = None
        self.name = f'[{lower_limit}, {upper_limit}]'


class SlitWidth(SettingOverWavelengthRange):
    """
    Slit width setting over a wavelength range.
    """

    m_def = Section(
        description='Slit width value over a wavelength range.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'wavelength_upper_limit',
                    'wavelength_lower_limit',
                    'value',
                ],
            ),
        ),
    )
    value = Quantity(
        type=np.float64,
        description='Slit width value.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
    )
    slit_width_servo = Quantity(
        type=bool,
        description="""
        True if slit width servo is on, i.e., the system monitors the reference
        beam energy and adjusts the slits to avoid over-saturation of the detectors.
        """,
        a_eln={'component': 'BoolEditQuantity'},
    )


class Monochromator(ArchiveSection):
    """
    Monochromator setting over a wavelength range.
    """

    m_def = Section(
        description='Monochromator setting over a wavelength range.',
    )
    monochromator_change_point = Quantity(
        type=np.float64,
        description='The wavelength at which the monochromator changes settings.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
        shape=['*'],
    )
    monochromator_slit_width = SubSection(
        section_def=SlitWidth,
        repeats=True,
    )


class Lamp(ArchiveSection):
    """
    Lamp setting over a wavelength range.
    """

    m_def = Section(
        description='Lamp setting over a wavelength range.',
    )
    d2_lamp = Quantity(
        type=bool,
        description=(
            'True if the Deuterium (D2) lamp is used '
            '(typically covers the UV range from about 160 nm to 400 nm).'
        ),
        a_eln={'component': 'BoolEditQuantity'},
    )
    tungsten_lamp = Quantity(
        type=bool,
        description=(
            'True if the Tungsten lamp is used '
            '(typically covers the visible to near-infrared range from about '
            '320 nm to 2500 nm)'
        ),
        a_eln={'component': 'BoolEditQuantity'},
    )
    lamp_change_point = Quantity(
        type=np.float64,
        description='The wavelength at which lamp used for the beam changes.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
        shape=['*'],
    )


class NIRGain(SettingOverWavelengthRange):
    """
    NIR gain factor over a range of wavelength.
    """

    m_def = Section(
        description='NIR gain factor over a wavelength range.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'wavelength_upper_limit',
                    'wavelength_lower_limit',
                    'value',
                ],
            ),
        ),
    )
    value = Quantity(
        type=np.float64,
        description='NIR gain factor of the detector.',
        a_eln={'component': 'NumberEditQuantity'},
        unit='dimensionless',
    )


class IntegrationTime(SettingOverWavelengthRange):
    """
    Integration time over a wavelength range.
    """

    m_def = Section(
        description='Integration time over a wavelength range.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'wavelength_upper_limit',
                    'wavelength_lower_limit',
                    'value',
                ],
            ),
        ),
    )
    value = Quantity(
        type=np.float64,
        description='Integration time value.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 's',
        },
        unit='s',
    )


class Detector(ArchiveSection):
    """
    Detector setting over a wavelength range.
    """

    m_def = Section(
        description='Detector setting over a wavelength range.',
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'module',
                    'detectors',
                    'detector_change_point',
                    'nir_gain',
                    'integration_time',
                ],
            ),
        ),
    )
    module = Quantity(
        type=MEnum(
            [
                'Three Detector Module',
                'Two Detector Module',
                '150-mm Integrating Sphere',
            ]
        ),
        a_eln={'component': 'EnumEditQuantity'},
        description="""
        Modules containing multiple detectors for different wavelength ranges.
        | Detector Module                      | Description          |
        |--------------------------------------|----------------------|
        | **Three Detector Module**            | Installed as standard module on Perkin-Elmer Lambda 1050 WB and NB spectrophotometers. Contains three detectors for different wavelength ranges: PMT, InGaAs, PbS. |
        | **Two Detector Module**              | Installed on Perkin-Elmer Lambda 750, 900, 950 spectrophotometers. Contains two detectors for different wavelength ranges: PMT, PbS. |
        | **150-mm Integrating Sphere**        | Includes an integrating sphere with a diameter of 150 mm which is equipped with PMT (R928) and InGaAs detector. The PMT covers 200-860.8 nm and the InGaAs detector covers 860.8-2500 nm. |
        """,  # noqa: E501
    )
    detectors = Quantity(
        type=str,
        description="""
        Detectors used in the instrument. Some of the popular detectors are:
        | Detector          | Description          |
        |-------------------|----------------------|
        | **PMT**           | Photomultiplier Tube detector used for the Ultra-Violet (UV) or visible range.|
        | **InGaAs**        | Indium Gallium Arsenide detector used for Near-Infra-red (NIR) range.|
        | **PbS**           | Lead Sulphide detector used for Infrared (IR) range.|
        """,  # noqa: E501
        a_eln={'component': 'StringEditQuantity'},
        shape=['*'],
    )
    detector_change_point = Quantity(
        type=np.float64,
        description='The wavelength at which the detector module changes.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
        shape=['*'],
    )
    nir_gain = SubSection(
        section_def=NIRGain,
        repeats=True,
    )
    integration_time = SubSection(
        section_def=IntegrationTime,
        repeats=True,
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        if self.module is not None:
            if self.module == 'Three Detector Module':
                self.detectors = ['PMT', 'InGaAs', 'PbS']
            elif self.module == 'Two Detector Module':
                self.detectors = ['PMT', 'PbS']
            elif self.module == '150-mm Integrating Sphere':
                self.detectors = ['PMT', 'InGaAs']


class Attenuator(ArchiveSection):
    """
    Attenuation setting for the sample and reference beam.
    """

    m_def = Section(
        description='Attenuation setting for the sample and reference beam.',
    )
    sample = Quantity(
        type=int,
        description='Sample beam attenuation in percentage.',
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )
    reference = Quantity(
        type=int,
        description='Reference beam attenuation in percentage.',
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )


class TransmissionSettings(ArchiveSection):
    """
    Section for setting of the instrument used for transmission measurement.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'ordinate_type',
                    'sample_beam_position',
                    'common_beam_mask',
                    'common_beam_depolarizer',
                ],
            ),
        ),
    )
    ordinate_type = Quantity(
        type=MEnum(['%T', 'A']),
        description=(
            'Specifies whether the ordinate (y-axis) of the measurement data is '
            'percent transmittance (%T) or absorbance (A).'
        ),
        a_eln={'component': 'EnumEditQuantity'},
    )
    sample_beam_position = Quantity(
        type=MEnum(['Front', 'Rear']),
        description=(
            'Position of the sample beam: either the front or the back of the sample '
            'chamber.'
        ),
        a_eln={'component': 'EnumEditQuantity'},
    )
    common_beam_mask = Quantity(
        type=int,
        description=(
            'Mask setting for the common beam in percentage.'
            '100% means the mask is fully open and '
            '100% of the beam passes. 0% means the mask is closed and no light passes.'
        ),
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )
    common_beam_depolarizer = Quantity(
        type=bool,
        description=(
            'True if the common beam depolarizer (CBD) is on, else False. CBD is an '
            'optional accessory used to depolarize the radiation coming from the '
            'monochromator.'
        ),
        default=False,
        a_eln={'component': 'BoolEditQuantity'},
    )
    accessory = SubSection(
        section_def=Accessory,
        repeats=True,
    )
    monochromator = SubSection(
        section_def=Monochromator,
    )
    lamp = SubSection(
        section_def=Lamp,
    )
    detector = SubSection(
        section_def=Detector,
    )
    attenuator = SubSection(
        section_def=Attenuator,
    )


class UVVisNirTransmissionResult(MeasurementResult):
    """
    Section for the results of the UV-Vis NIR Transmission measurement.
    """

    m_def = Section(
        a_eln={'hide': ['array_index']},
    )
    array_index = Quantity(
        type=int,
        description='Array of indices used for plotting quantity vectors.',
        shape=['*'],
    )
    transmittance = Quantity(
        type=np.float64,
        description='Measured transmittance in percentage.',
        shape=['*'],
        unit='dimensionless',
        a_plot={'x': 'array_index', 'y': 'transmittance'},
    )
    absorbance = Quantity(
        type=np.float64,
        description='Measured absorbance ranging from 0 to 1.',
        shape=['*'],
        unit='dimensionless',
        a_plot={'x': 'array_index', 'y': 'absorbance'},
    )
    extinction_coefficient = Quantity(
        type=np.float64,
        description=(
            'Extinction coefficient calculated from transmittance and sample thickness '
            'values: -log(T)/L. The coefficient includes the effects of '
            'absorption, reflection, and scattering.'
        ),
        shape=['*'],
        unit='1/cm',
        a_plot={'x': 'array_index', 'y': 'extinction_coefficient'},
    )
    wavelength = Quantity(
        type=np.float64,
        description='Wavelength values for which the measurement was conducted.',
        shape=['*'],
        unit='nm',
        a_plot={'x': 'array_index', 'y': 'wavelength'},
    )

    def generate_plots(self) -> list[PlotlyFigure]:
        """
        Generate the plotly figures for the `UVVisNirTransmissionResult` section.

        Returns:
            list[PlotlyFigure]: The plotly figures.
        """
        figures = []
        if self.wavelength is None:
            return figures

        for key in ['transmittance', 'absorbance', 'extinction_coefficient']:
            if getattr(self, key) is None:
                continue

            y = getattr(self, key).magnitude
            y_label = key.replace('_', ' ').capitalize()

            line_linear = px.line(
                x=self.wavelength.to('nm').magnitude,
                y=y,
            )
            line_linear.update_layout(
                title=f'{y_label} over Wavelength',
                xaxis_title='Wavelength (nm)',
                yaxis_title=y_label,
                xaxis=dict(
                    fixedrange=False,
                ),
                yaxis=dict(
                    fixedrange=False,
                ),
                template='plotly_white',
            )
            figures.append(
                PlotlyFigure(
                    label=f'{y_label} linear plot',
                    figure=line_linear.to_plotly_json(),
                ),
            )

        return figures

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `UVVisNirTransmissionResult` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        if archive.data.samples:
            sample = archive.data.samples[0]
            if sample.reference is None:
                logger.warn('No reference sample found.')
            if sample.reference.get('length') is not None:
                if self.get('transmittance') is not None:
                    self.extinction_coefficient = -np.log(
                        self.transmittance / 100
                    ) / sample.reference.length.to('cm')
                return
        # reset absorption coefficient if required conditions are not met
        if archive.data.results:
            if archive.data.results[0].get('extinction_coefficient') is not None:
                archive.data.results[0].extinction_coefficient = None


class UVVisTransmission(Measurement):
    """
    Schema for UV-Vis NIR Transmission, which extends the basesection Measurement.
    """

    m_def = Section()
    method = Quantity(
        type=str,
        default='UV-Vis-NIR Transmission',
    )
    user = Quantity(
        type=str,
        description='Name of user or analyst.',
        a_eln={'component': 'StringEditQuantity'},
    )
    results = Measurement.results.m_copy()
    results.section_def = UVVisNirTransmissionResult

    transmission_settings = SubSection(
        section_def=TransmissionSettings,
    )


class ELNUVVisTransmission(UVVisTransmission, PlotSection, EntryData):
    """
    Entry class for UVVisTransmission. Handles the population of the schema and
    plotting. Data is added either through manual input in the GUI or by parsing
    the measurement files coming from the instrument.
    """

    m_def = Section(
        label='UV-Vis-NIR Transmission',
        a_template={
            'measurement_identifiers': {},
        },
    )

    measurement_identifiers = SubSection(
        section_def=ReadableIdentifiers,
    )

    data_file = Quantity(
        type=str,
        description='File generated by the instrument containing data and metadata.',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.FileEditQuantity,
        ),
    )

    def get_read_write_functions(self) -> tuple[Callable, Callable]:
        """
        Method for getting the correct read and write functions for the current data
        file.

        Returns:
            tuple[Callable, Callable]: The read, write functions.
        """
        if self.data_file.endswith('.asc'):
            return read_asc, self.write_transmission_data
        return None, None

    def create_instrument_entry(
        self, data_dict: dict[str, Any], archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> InstrumentReference:
        """
        Method for creating the instrument entry. Returns a reference to the created
        instrument.

        Args:
            data_dict (Dict[str, Any]): The dictionary containing the instrument data.
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.

        Returns:
            InstrumentReference: The instrument reference.
        """
        instrument = TransmissionSpectrophotometer(
            name=data_dict['instrument_name'],
            serial_number=data_dict['instrument_serial_number'],
            software_version=data_dict['instrument_firmware_version'],
        )
        if data_dict['start_datetime'] is not None:
            instrument.datetime = data_dict['start_datetime']
        instrument.normalize(archive, logger)

        logger.info('Created instrument entry.')
        m_proxy_value = create_archive(instrument, archive, 'instrument.archive.json')

        return InstrumentReference(reference=m_proxy_value)

    def get_instrument_reference(
        self, data_dict: dict[str, Any], archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> Union[InstrumentReference, None]:
        """
        Method for getting the instrument reference.
        Looks for an existing instrument with the given serial number.
        If found, it returns a reference to this instrument.
        If no instrument is found, logs a warning, creates a new entry for the
        instrument and returns a reference to this entry.
        If multiple instruments are found, it logs a warning and returns None.

        Args:
            data_dict (Dict[str, Any]): The dictionary containing the instrument data.
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.

        Returns:
            Union[InstrumentReference, None]: The instrument reference or None.
        """
        from nomad.search import search

        serial_number = data_dict['instrument_serial_number']
        api_query = {
            'search_quantities': {
                'id': (
                    'data.serial_number#uv_vis_nir_transmission.schema.'
                    'TransmissionSpectrophotometer'
                ),
                'str_value': f'{serial_number}',
            },
        }
        search_result = search(
            owner='visible',
            query=api_query,
            user_id=archive.metadata.main_author.user_id,
        )

        if not search_result.data:
            logger.warn(
                f'No "TransmissionSpectrophotometer" instrument found with the serial '
                f'number "{serial_number}".'
            )
            return self.create_instrument_entry(data_dict, archive, logger)

        if len(search_result.data) > 1:
            logger.warn(
                f'Multiple "TransmissionSpectrophotometer" instruments found with the '
                f'serial number "{serial_number}". Please select it manually.'
            )
            return None

        entry = search_result.data[0]
        upload_id = entry['upload_id']
        entry_id = entry['entry_id']
        m_proxy_value = f'../uploads/{upload_id}/archive/{entry_id}#/data'

        return InstrumentReference(reference=m_proxy_value)

    def write_transmission_data(  # noqa: PLR0912, PLR0915
        self,
        transmission_dict: dict[str, Any],
        archive: 'EntryArchive',
        logger: 'BoundLogger',
    ) -> None:
        """
        Populate `UVVisTransmission` section with the data from the transmission_dict.

        Args:
            transmission_dict (Dict[str, Any]): A dictionary with the transmission data.
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        """
        self.user = transmission_dict['analyst_name']
        if transmission_dict['start_datetime'] is not None:
            self.datetime = transmission_dict['start_datetime']

        result = UVVisNirTransmissionResult(
            wavelength=transmission_dict['measured_wavelength'],
        )
        if transmission_dict['ordinate_type'] == 'A':
            result.absorbance = transmission_dict['measured_ordinate']
        elif transmission_dict['ordinate_type'] == '%T':
            result.transmittance = transmission_dict['measured_ordinate']
        else:
            logger.warn(f"Unknown ordinate type '{transmission_dict['ordinate']}'.")
        result.normalize(archive, logger)

        lamp = Lamp(
            d2_lamp=transmission_dict['is_d2_lamp_used'],
            tungsten_lamp=transmission_dict['is_tungsten_lamp_used'],
            lamp_change_point=transmission_dict['lamp_change_wavelength'],
        )
        lamp.normalize(archive, logger)

        detector_module = transmission_dict['detector_module']
        if detector_module == 'uv/vis/nir detector':
            if 'lambda 1050' in transmission_dict['instrument_name'].lower():
                detector_module = 'Three Detector Module'
            elif 'lambda 950' in transmission_dict['instrument_name'].lower():
                detector_module = 'Two Detector Module'
            elif 'lambda 900' in transmission_dict['instrument_name'].lower():
                detector_module = 'Two Detector Module'
            elif 'lambda 750' in transmission_dict['instrument_name'].lower():
                detector_module = 'Two Detector Module'
        if detector_module == '150mm sphere':
            detector_module = '150-mm Integrating Sphere'
        detector = Detector(
            module=detector_module,
        )
        for idx, wavelength_value in enumerate(transmission_dict['detector_NIR_gain']):
            nir_gain = NIRGain(
                wavelength_upper_limit=wavelength_value['wavelength'],
                value=wavelength_value['value'],
            )
            if idx + 1 < len(transmission_dict['detector_NIR_gain']):
                nir_gain.wavelength_lower_limit = transmission_dict[
                    'detector_NIR_gain'
                ][idx + 1]['wavelength']
            nir_gain.normalize(archive, logger)
            detector.nir_gain.append(nir_gain)
        for idx, wavelength_value in enumerate(
            transmission_dict['detector_integration_time']
        ):
            integration_time = IntegrationTime(
                wavelength_upper_limit=wavelength_value['wavelength'],
                value=wavelength_value['value'],
            )
            if idx + 1 < len(transmission_dict['detector_integration_time']):
                integration_time.wavelength_lower_limit = transmission_dict[
                    'detector_integration_time'
                ][idx + 1]['wavelength']
            integration_time.normalize(archive, logger)
            detector.integration_time.append(integration_time)

        detector.detector_change_point = transmission_dict['detector_change_wavelength']
        detector.normalize(archive, logger)

        monochromator = Monochromator()
        for idx, wavelength_value in enumerate(
            transmission_dict['monochromator_slit_width']
        ):
            slit_width = SlitWidth(
                wavelength_upper_limit=wavelength_value['wavelength'],
            )
            if (
                isinstance(wavelength_value['value'], str)
                and wavelength_value['value'].lower() == 'servo'
            ):
                slit_width.value = None
                slit_width.slit_width_servo = True
            elif isinstance(wavelength_value['value'], ureg.Quantity):
                slit_width.value = wavelength_value['value']
                slit_width.slit_width_servo = False
            else:
                logger.warning(
                    f'Invalid slit width value "{wavelength_value["value"]}" for '
                    f'wavelength "{wavelength_value["wavelength"]}".'
                )
                continue
            if idx + 1 < len(transmission_dict['monochromator_slit_width']):
                slit_width.wavelength_lower_limit = transmission_dict[
                    'monochromator_slit_width'
                ][idx + 1]['wavelength']
            slit_width.normalize(archive, logger)
            monochromator.monochromator_slit_width.append(slit_width)
        monochromator.monochromator_change_point = transmission_dict[
            'monochromator_change_wavelength'
        ]
        monochromator.normalize(archive, logger)

        attenuator = Attenuator(
            sample=transmission_dict['attenuation_percentage']['sample'],
            reference=transmission_dict['attenuation_percentage']['reference'],
        )

        if self.get('transmission_settings'):
            if self.transmission_settings.get('accessory'):
                for idx, accessory in enumerate(self.transmission_settings.accessory):
                    if isinstance(accessory, PolDepol):
                        if accessory.mode == 'Polarizer':
                            self.transmission_settings.accessory[
                                idx
                            ].polarizer_angle = transmission_dict['polarizer_angle']

        transmission_settings = TransmissionSettings(
            ordinate_type=transmission_dict['ordinate_type'],
            sample_beam_position=transmission_dict['sample_beam_position'],
            common_beam_mask=transmission_dict['common_beam_mask_percentage'],
            common_beam_depolarizer=transmission_dict['is_common_beam_depolarizer_on'],
            lamp=lamp,
            detector=detector,
            monochromator=monochromator,
            attenuator=attenuator,
        )
        transmission_settings.normalize(archive, logger)

        instrument_reference = self.get_instrument_reference(
            transmission_dict, archive, logger
        )
        if instrument_reference is not None:
            instruments = [instrument_reference]
        else:
            instruments = []

        transmission = UVVisTransmission(
            results=[result],
            transmission_settings=transmission_settings,
            instruments=instruments,
        )
        merge_sections(self, transmission, logger)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        """
        The normalize function of the `UVVisTransmission` section.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        if self.data_file is not None:
            read_function, write_function = self.get_read_write_functions()
            if read_function is None or write_function is None:
                logger.warn(
                    f'No compatible reader found for the file: "{self.data_file}".'
                )
            else:
                with archive.m_context.raw_file(self.data_file) as file:
                    transmission_dict = read_function(file.name, logger)
                write_function(transmission_dict, archive, logger)
        super().normalize(archive, logger)

        if not self.results:
            return

        self.figures = self.results[0].generate_plots()


m_package.__init_metainfo__()
