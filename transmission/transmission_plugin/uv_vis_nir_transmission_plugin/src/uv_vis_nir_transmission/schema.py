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
)
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import CompositeSystem
from nomad.datamodel.metainfo.basesections import Instrument
from nomad.datamodel.metainfo.basesections import Measurement
from nomad.datamodel.metainfo.basesections import MeasurementResult
import numpy as np
import plotly.express as px
from structlog.stdlib import (
    BoundLogger,
)
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

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad.datamodel.metainfo.plot import (
    PlotSection,
    PlotlyFigure,
)

from uv_vis_nir_transmission.readers import read_asc
from uv_vis_nir_transmission.utils import merge_sections

m_package = Package(name="uv-vis-nir-transmission")


class UVVisNirTransmissionResult(MeasurementResult, ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    type = Quantity(
        type=str,  # MEnum(["Transmission", "Absorbance"]),
        description="type of measurement",
        # a_eln={"component": "RadioEnumEditQuantity"},
    )
    transmission = Quantity(
        type=np.float64,
        description="transmittance",
        # a_eln={"component": "NumberEditQuantity"},
        shape=["*"],
        a_plot={"x": "wavelength", "y": "transmission"},
    )
    wavelength = Quantity(
        type=np.float64,
        description="wavelength",
        # a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "nm"},
        shape=["*"],
        unit="nm",
        a_plot={"x": "wavelength", "y": "transmission"},
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `UVVisNirTransmissionResult` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(UVVisNirTransmissionResult, self).normalize(archive, logger)


class Accessory(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    polarizer = Quantity(
        type=bool,
        description="polarizer used",
        a_eln={"component": "BoolEditQuantity"},
    )
    aperture = Quantity(
        type=np.float64,
        description="aperture diameter",
        a_eln={"component": "NumberEditQuantity"},
        unit="mm",
    )


class SlitWidth(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    wavelength = Quantity(
        type=np.float64,
        description="wavelength",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )
    value = Quantity(
        type=np.float64,
        description="slit width",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )


class Monochromator(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    monochromator_change_point = Quantity(
        type=np.float64,
        description="monochromator change point in nm",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )
    slit_width = SubSection(
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
        description="D2 lamp used",
        a_eln={"component": "BoolEditQuantity"},
    )
    tungsten_lamp = Quantity(
        type=bool,
        description="tungsten lamp used",
        a_eln={"component": "BoolEditQuantity"},
    )
    lamp_change_point = Quantity(
        type=np.float64,
        description="lamp change point in nm",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )


class NirGain(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    wavelength = Quantity(
        type=np.float64,
        description="wavelength",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )
    value = Quantity(
        type=np.float64,
        description="value",
        a_eln={"component": "NumberEditQuantity"},
    )


class IntegrationTime(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    wavelength = Quantity(
        type=np.float64,
        description="wavelength",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )
    value = Quantity(
        type=np.float64,
        description="value",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "s"},
        unit="s",
    )


class Detector(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    module = Quantity(
        type=MEnum(["three detector module", "150mm integrating sphere"]),
        description="detector module",
        a_eln={"component": "RadioEnumEditQuantity"},
    )
    detector_change_point = Quantity(
        type=np.float64,
        description="detector change point in nm",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "nm"},
        unit="nm",
    )
    nir_gain = SubSection(
        section_def=NirGain,
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
        description="sample beam attenuation in %",
        a_eln={"component": "NumberEditQuantity", "minValue": 0, "maxValue": 100},
    )
    reference = Quantity(
        type=int,
        description="reference beam attenuation in %",
        a_eln={"component": "NumberEditQuantity"},
    )


class InstrumentSettings(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    ordinate_type = Quantity(
        type=MEnum(["%T", "A"]),
        description="ordinate type",
        a_eln={"component": "RadioEnumEditQuantity"},
    )
    sample_beam_position = Quantity(
        type=MEnum(["Front", "Rear"]),
        description="sample beam position",
        a_eln={"component": "RadioEnumEditQuantity"},
    )
    common_beam_mask = Quantity(
        type=int,
        description="common beam mask",
        a_eln={"component": "NumberEditQuantity", "minValue": 0, "maxValue": 100},
    )
    common_beam_depolarizer = Quantity(
        type=bool,
        description="common beam depolarizer",
        a_eln={"component": "BoolEditQuantity"},
    )
    polarizer_angle = Quantity(
        type=np.float64,
        description="polarizer angle in °",
        a_eln={"component": "NumberEditQuantity"},
        unit="degrees",
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


class UVVisTransmission(Measurement, PlotSection, EntryData, ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    user = Quantity(
        type=str,
        description="analyst name from header in ascii",
        a_eln={"component": "StringEditQuantity"},
    )
    data_file = Quantity(
        type=str,
        description="*.asc Data file containing the UV-Vis-NIR transmission spectrum",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.FileEditQuantity,
        ),
    )
    results = SubSection(
        section_def=UVVisNirTransmissionResult,
        repeats=True,
    )
    instrument_settings = SubSection(
        section_def=InstrumentSettings,
    )

    def get_read_write_functions(self) -> tuple[Callable, Callable]:
        """
        Method for getting the correct read and write functions for the current data file.

        Returns:
            tuple[Callable, Callable]: The read, write functions.
        """
        if self.data_file.endswith(".asc"):
            return read_asc, self.write_nx_transmission
        return None, None

    def write_nx_transmission(
        self,
        transmission_dict: "Template",
        archive: "EntryArchive",
        logger: "BoundLogger",
    ) -> None:
        """
        Populate `UVVisTransmission` section from a NeXus Template.

        Args:
            transmission_dict (Dict[str, Any]): A dictionary with the transmission data.
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        """
        result = UVVisNirTransmissionResult(
            type=transmission_dict.get(
                "/ENTRY[entry]/data/type",
                None,
            ),
            transmission=transmission_dict.get(
                "/ENTRY[entry]/data/transmission",
                None,
            ),
            wavelength=transmission_dict.get(
                "/ENTRY[entry]/data/wavelength",
                None,
            ),
        )
        result.normalize(archive, logger)

        transmission = UVVisTransmission(
            results=[result],
        )
        merge_sections(self, transmission, logger)

        nexus_output = None
        # if self.generate_nexus_file:
        #     archive_name = archive.metadata.mainfile.split('.')[0]
        #     nexus_output = f'{archive_name}_output.nxs'
        # handle_nexus_subsection(
        #     transmission_dict,
        #     nexus_output,
        #     archive,
        #     logger,
        # )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger"):
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

        line_linear = px.line(
            x=self.results[0].wavelength,
            y=self.results[0].transmission,
            labels={
                "x": "Wavelength (nm)",
                "y": "Transmission",
            },
            title="Transmission",
        )
        self.figures.extend(
            [
                PlotlyFigure(
                    label="Linear Plot",
                    # index=2,
                    figure=line_linear.to_plotly_json(),
                ),
            ]
        )

    # def normalize(self, archive, logger: BoundLogger) -> None:
    #     """
    #     The normalizer for the `UVVisTransmission` class.

    #     Args:
    #         archive (EntryArchive): The archive containing the section that is being
    #         normalized.
    #         logger (BoundLogger): A structlog logger.
    #     """
    #     super(UVVisTransmission, self).normalize(archive, logger)


class PerkinElmerLambda1050(Instrument, EntryData, ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    name = Quantity(
        type=str,
        description="instrument name",
        a_eln={"component": "StringEditQuantity", "label": "instrument_name"},
    )
    lab_id = Quantity(
        type=str,
        description="instrument serial number",
        a_eln={"component": "StringEditQuantity", "label": "instrument_serial_number"},
    )
    software_version = Quantity(
        type=str,
        description="software/firmware version",
        a_eln={"component": "StringEditQuantity"},
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `PerkinElmerLambda1050` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(PerkinElmerLambda1050, self).normalize(archive, logger)


class TransmissionSample(CompositeSystem, EntryData, ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    name = Quantity(
        type=str,
        description="sample name",
        a_eln={"component": "StringEditQuantity", "label": "sample_name"},
    )
    lab_id = Quantity(
        type=str,
        description="sample id",
        a_eln={"component": "StringEditQuantity", "label": "sample_id"},
    )
    chemical_composition = Quantity(
        type=str,
        description="chemical composition",
        a_eln={"component": "StringEditQuantity"},
    )
    length = Quantity(
        type=np.float64,
        description="length (or thickness) of the sample in mm",
        a_eln={"component": "NumberEditQuantity"},  # "defaultDisplayUnit": "mm"},
        unit="mm",
    )
    orientation = Quantity(
        type=str,
        description="crystallographic orientation of sample",
        a_eln={"component": "StringEditQuantity"},
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `TransmissionSample` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(TransmissionSample, self).normalize(archive, logger)


m_package.__init_metainfo__()
