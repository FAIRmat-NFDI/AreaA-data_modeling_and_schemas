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
    Dict,
    Any,
    Callable,
    Union,
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    Instrument,
    InstrumentReference,
    Measurement,
    MeasurementResult,
    ReadableIdentifiers,
)
import numpy as np
import plotly.express as px
from nomad.metainfo import (
    Package,
    Quantity,
    SubSection,
    MEnum,
    Section,
)
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
)
from nomad.units import ureg

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad.datamodel.metainfo.plot import (
    PlotSection,
    PlotlyFigure,
)

from uv_vis_nir_transmission.readers import read_asc
from uv_vis_nir_transmission.utils import merge_sections, create_archive

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger


m_package = Package(name='uv-vis-nir-transmission')


class TransmissionSpectrophotometer(Instrument, EntryData):
    """
    Entry section for the transmission spectrophotometer.
    """

    m_def = Section()
    serial_number = Quantity(
        type=str,
        description='instrument serial number',
        a_eln={'component': 'StringEditQuantity'},
    )
    software_version = Quantity(
        type=str,
        description='software/firmware version',
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


class TransmissionSample(CompositeSystem, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    name = Quantity(
        type=str,
        description='sample name',
        a_eln={'component': 'StringEditQuantity', 'label': 'sample_name'},
    )
    lab_id = Quantity(
        type=str,
        description='sample id',
        a_eln={'component': 'StringEditQuantity', 'label': 'sample_id'},
    )
    chemical_composition = Quantity(
        type=str,
        description='chemical composition',
        a_eln={'component': 'StringEditQuantity'},
    )
    length = Quantity(
        type=np.float64,
        description='length (or thickness) of the sample in mm',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'mm',
        },
        unit='mm',
    )
    orientation = Quantity(
        type=str,
        description='crystallographic orientation of sample',
        a_eln={'component': 'StringEditQuantity'},
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `TransmissionSample` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(TransmissionSample, self).normalize(archive, logger)


class Accessory(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    polarizer = Quantity(
        type=bool,
        description='polarizer used',
        a_eln={'component': 'BoolEditQuantity'},
    )
    aperture = Quantity(
        type=np.float64,
        description='aperture diameter',
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
        a_display={
            'order': [
                'name',
                'wavelength_upper_limit',
                'wavelength_lower_limit',
                'value',
            ]
        },
    )
    name = Quantity(
        type=str,
        description='Short description containing wavelength range',
        a_eln={'component': 'StringEditQuantity'},
    )
    wavelength_upper_limit = Quantity(
        type=np.float64,
        description='Upper limit of wavelength in nm.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
    )
    wavelength_lower_limit = Quantity(
        type=np.float64,
        description='Lower limit of wavelength in nm.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
    )
    value = Quantity(
        type=np.float64,
        description='Value of the setting',
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

        right_limit = '-'
        left_limit = '-'
        if self.wavelength_upper_limit is not None:
            right_limit = self.wavelength_upper_limit.magnitude
        if self.wavelength_lower_limit is not None:
            left_limit = self.wavelength_lower_limit.magnitude
        self.name = f'[{left_limit}, {right_limit}]'


class SlitWidth(SettingOverWavelengthRange):
    """
    Slit width setting over a range of wavelength.
    """

    m_def = Section()
    value = Quantity(
        type=np.float64,
        description='Value of slit width over a range of wavelength.',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
    )
    slit_width_servo = Quantity(
        type=bool,
        description='True if slit width servo is on, i.e., the slit width varies.',
        a_eln={'component': 'BoolEditQuantity'},
    )


class Monochromator(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    monochromator_change_point = Quantity(
        type=np.float64,
        description='monochromator change point in nm',
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
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    d2_lamp = Quantity(
        type=bool,
        description='D2 lamp used',
        a_eln={'component': 'BoolEditQuantity'},
    )
    tungsten_lamp = Quantity(
        type=bool,
        description='tungsten lamp used',
        a_eln={'component': 'BoolEditQuantity'},
    )
    lamp_change_point = Quantity(
        type=np.float64,
        description='lamp change point in nm',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'nm',
        },
        unit='nm',
        shape=['*'],
    )


class NIRGain(SettingOverWavelengthRange):
    """
    NIR gain setting over a range of wavelength.
    """

    m_def = Section(
        description='NIR gain over a range of wavelength.',
    )
    value = Quantity(
        type=np.float64,
        description='NIR gain value.',
        a_eln={'component': 'NumberEditQuantity'},
        unit='dimensionless',
    )


class IntegrationTime(SettingOverWavelengthRange):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        description='Integration time for a given wavelength range.',
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
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    module = Quantity(
        type=MEnum(['three detector module', '150-mm integrating sphere']),
        description='detector module',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )
    detector_change_point = Quantity(
        type=np.float64,
        description='detector change point in nm',
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


class Attenuator(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    sample = Quantity(
        type=int,
        description='sample beam attenuation in %',
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )
    reference = Quantity(
        type=int,
        description='reference beam attenuation in %',
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )


class TransmissionSettings(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    ordinate_type = Quantity(
        type=MEnum(['%T', 'A']),
        description='ordinate type',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )
    sample_beam_position = Quantity(
        type=MEnum(['Front', 'Rear']),
        description='sample beam position',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )
    common_beam_mask = Quantity(
        type=int,
        description='common beam mask',
        a_eln={
            'component': 'NumberEditQuantity',
            'minValue': 0,
            'maxValue': 100,
        },
        unit='dimensionless',
    )
    common_beam_depolarizer = Quantity(
        type=bool,
        description='common beam depolarizer',
        a_eln={'component': 'BoolEditQuantity'},
    )
    polarizer_angle = Quantity(
        type=np.float64,
        description='polarizer angle in °',
        a_eln={'component': 'NumberEditQuantity'},
        unit='degrees',
    )
    accessory = SubSection(
        section_def=Accessory,
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
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    transmittance = Quantity(
        type=np.float64,
        description='Transmittance percentage %T',
        shape=['*'],
        unit='dimensionless',
        a_plot={'x': 'wavelength', 'y': 'transmittance'},
    )
    absorbance = Quantity(
        type=np.float64,
        description='Absorbance A',
        shape=['*'],
        unit='dimensionless',
        a_plot={'x': 'wavelength', 'y': 'absorbance'},
    )
    wavelength = Quantity(
        type=np.float64,
        description='wavelength',
        shape=['*'],
        unit='nm',
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

        for key in ['transmittance', 'absorbance']:
            if getattr(self, key) is None:
                continue

            y = getattr(self, key).magnitude
            y_label = key.capitalize()

            line_linear = px.line(
                x=self.wavelength.to('nm').magnitude,
                y=y,
            )
            line_linear.update_layout(
                title=f'{y_label} vs wavelength',
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
                    label=f'{y_label} Linear Plot',
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
        super(UVVisNirTransmissionResult, self).normalize(archive, logger)


class UVVisTransmission(Measurement):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    method = Quantity(
        type=str,
        default='UV-Vis-NIR Transmission',
    )
    user = Quantity(
        type=str,
        description='analyst name from header in ascii',
        a_eln={'component': 'StringEditQuantity'},
    )
    results = Measurement.results.m_copy()
    results.section_def = UVVisNirTransmissionResult

    transmission_settings = SubSection(
        section_def=TransmissionSettings,
    )


class ELNUVVisTransmission(UVVisTransmission, PlotSection, EntryData):
    """
    Entry class for UVVisTransmission.
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
        description='Data file containing the UV-Vis-NIR transmission spectrum',
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.FileEditQuantity,
        ),
    )

    def get_read_write_functions(self) -> tuple[Callable, Callable]:
        """
        Method for getting the correct read and write functions for the current data file.

        Returns:
            tuple[Callable, Callable]: The read, write functions.
        """
        if self.data_file.endswith('.asc'):
            return read_asc, self.write_transmission_data
        return None, None

    def create_instrument_entry(
        self, data_dict: Dict[str, Any], archive: 'EntryArchive', logger: 'BoundLogger'
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
        self, data_dict: Dict[str, Any], archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> Union[InstrumentReference, None]:
        """
        Method for getting the instrument reference.
        Looks for an existing instrument with the given serial number.
        If found, it returns a reference to this instrument.
        If no instrument is found, logs a warning, creates a new entry for the instrument
        and returns a reference to this entry.
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

    def write_transmission_data(
        self,
        transmission_dict: Dict[str, Any],
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

        detector = Detector(
            module=transmission_dict['detector_module'],
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

        transmission_settings = TransmissionSettings(
            ordinate_type=transmission_dict['ordinate_type'],
            sample_beam_position=transmission_dict['sample_beam_position'],
            common_beam_mask=transmission_dict['common_beam_mask_percentage'],
            common_beam_depolarizer=transmission_dict['is_common_beam_depolarizer_on'],
            polarizer_angle=transmission_dict['polarizer_angle'],
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

    # def normalize(self, archive, logger: BoundLogger) -> None:
    #     """
    #     The normalizer for the `UVVisTransmission` class.

    #     Args:
    #         archive (EntryArchive): The archive containing the section that is being
    #         normalized.
    #         logger (BoundLogger): A structlog logger.
    #     """
    #     super(UVVisTransmission, self).normalize(archive, logger)


m_package.__init_metainfo__()
