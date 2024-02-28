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

from nomad.metainfo import Package, Quantity, MEnum, SubSection, Section, MSection
from nomad.datamodel.data import EntryData, ArchiveSection
from . import reader as hall_reader
from .measurement import GenericMeasurement, VariableFieldMeasurement
from .hall_instrument import Instrument
from .nexus_to_msection import get_measurements, get_instrument

from nomad.datamodel.metainfo.basesections import (
    ElementalComposition,
    Activity,
    PureSubstance,
    CompositeSystem,
    Measurement,
    Process,
    ProcessStep,
    MeasurementResult,
    Collection,
    EntityReference,
    Instrument,
    CompositeSystemReference,
    SectionReference,
    Experiment,
)

from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)

from ikz_plugin import IKZHallCategory

m_package = Package(name="hall_lakeshore")


class HallMeasurementResult(MeasurementResult):
    """
    Contains result quantities from Hall measurement
    """

    resistivity = Quantity(
        type=np.float64,
        description="FILL",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "ohm * cm"},
        unit="ohm * cm",
    )
    mobility = Quantity(
        type=np.float64,
        description="FILL",
        a_eln={
            "component": "NumberEditQuantity",
            "defaultDisplayUnit": "cm**2 / volt / second",
        },
        unit="cm**2 / volt / second",
    )
    carrier_concentration = Quantity(
        type=np.float64,
        description="FILL",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "1 / cm**3"},
        unit="1 / cm**3",
    )


class HallMeasurement(Measurement, EntryData):
    """
    A parser for hall measurement data
    """

    m_def = Section(
        a_eln={"hide": ["steps"]},
        categories=[IKZHallCategory],
    )
    data_file = Quantity(
        type=str,
        a_eln=dict(component="FileEditQuantity"),
        a_browser=dict(adaptor="RawFileAdaptor"),
    )
    description = Quantity(
        type=str,
        description="description",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Notes",
        ),
    )

    measurements = SubSection(section_def=GenericMeasurement, repeats=True)

    results = SubSection(
        section_def=HallMeasurementResult,
        description="""
        The result of the measurement.
        """,
        repeats=True,
    )

    def normalize(self, archive, logger):
        super(HallMeasurement, self).normalize(archive, logger)

        if not self.data_file:
            return

        logger.info("Parsing hall measurement measurement file.")
        with archive.m_context.raw_file(
            self.data_file, "r", encoding="unicode_escape"
        ) as f:
            data_template = hall_reader.parse_txt(f.name)
            self.measurements = list(get_measurements(data_template))

        for measurement in self.measurements:
            if isinstance(measurement, VariableFieldMeasurement):
                if (
                    measurement.measurement_type == "Hall and Resistivity Measurement"
                    and measurement.maximum_field == measurement.minimum_field
                ):
                    logger.info(
                        "This measurement was detected as a single Field Room Temperature one."
                    )
                    self.results.append(
                        HallMeasurementResult(
                            name="Room Temperature measurement",
                            resistivity=measurement.data[0].resistivity,
                            mobility=measurement.data[0].hall_mobility,
                            carrier_concentration=measurement.data[0].carrier_density,
                        )
                    )


class HallMeasurementReference(SectionReference):
    """
    A section used for referencing a HallMeasurement.
    """

    reference = Quantity(
        type=HallMeasurement,
        description="A reference to a NOMAD `HallMeasurement` entry.",
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Hall Measurement Reference",
        ),
    )


class HallInstrument(Instrument, EntryData):
    """
    Representation of an instrument
    """

    m_def = Section(
        categories=[IKZHallCategory],
    )
    data_file = Quantity(
        type=str,
        a_eln=dict(component="FileEditQuantity"),
        a_browser=dict(adaptor="RawFileAdaptor"),
    )

    instrument = SubSection(section_def=Instrument)

    def normalize(self, archive, logger):
        super(HallInstrument, self).normalize(archive, logger)

        if not self.data_file:
            return

        logger.info("Parsing hall measurement instrument file.")
        with archive.m_context.raw_file(
            self.data_file, "r", encoding="unicode_escape"
        ) as f:
            data_template = hall_reader.parse_txt(f.name)
            self.instrument = get_instrument(data_template, logger)


class HallInstrumentReference(SectionReference):
    """
    A section used for referencing a HallInstrument.
    """

    reference = Quantity(
        type=HallInstrument,
        description="A reference to a NOMAD `HallInstrument` entry.",
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Hall Instrument Reference",
        ),
    )


class ContactsGraftingStep(ProcessStep):
    """Class autogenerated from yaml schema."""

    m_def = Section(a_eln=None)
    step_type = Quantity(
        type=MEnum(
            ["Pre-process", "Process", "Post-process", "Measurement", "Storage"]
        ),
        a_eln={"component": "EnumEditQuantity"},
    )

    step_number = Quantity(
        type=int,
        description="sequential number of the step on going",
        a_eln={"component": "NumberEditQuantity"},
    )

    elapsed_time = Quantity(
        type=np.float64,
        description="Duration of the current step",
        unit="minute",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "minute"},
    )


class ContactsGrafting(Process, EntryData):
    """Class autogenerated from yaml schema."""

    m_def = Section(
        categories=[IKZHallCategory],
    )
    method = Quantity(
        type=str,
        default="Contacts Grafting (IKZ)",
    )
    dose = Quantity(
        type=np.float64, description="dose", a_eln={"component": "NumberEditQuantity"}
    )

    net_mass_before = Quantity(
        type=np.float64,
        description="net mass before the process step",
        unit="gram",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram"},
    )

    crucible_model = Quantity(
        type=str,
        description="The name of the chemical that is typically used in literature",
        a_eln={"component": "StringEditQuantity"},
    )

    crucible_mass = Quantity(
        type=np.float64,
        description="crucible mass",
        unit="gram",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram"},
    )

    brutto_mass_before = Quantity(
        type=np.float64,
        description="brutto mass before the process step",
        unit="gram",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "gram"},
    )

    atmosphere = Quantity(
        type=str,
        description="which atmosphere is choosen for th experiment",
        a_eln={"component": "StringEditQuantity"},
    )

    oven = Quantity(
        type=str,
        description="oven used in the experiment",
        a_eln={"component": "StringEditQuantity"},
    )

    steps = SubSection(section_def=ContactsGraftingStep, repeats=True)


class ContactsGraftingReference(SectionReference):
    """
    A section used for referencing a ContactsGrafting.
    """

    reference = Quantity(
        type=ContactsGrafting,
        description="A reference to a NOMAD `ContactsGrafting` entry.",
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Contacts Grafting Reference",
        ),
    )


# this is not used yet
class MeasurementGeometry(ArchiveSection):
    """Class autogenerated from yaml schema."""

    m_def = Section()
    geometry = Quantity(
        type=MEnum(
            [
                "Van_der_Pauw_square",
                "Van_der_Pauw_rectangular",
                "Van_der_Pauw_arbitrary",
                "Hall_bar_1221",
                "Hall_bar_1311",
            ]
        ),
        a_eln={"component": "EnumEditQuantity"},
    )


# this is not used yet
class MetalStack(PureSubstance):
    """Class autogenerated from yaml schema."""

    m_def = Section()
    thickness = Quantity(
        type=np.float64,
        description="FILL THE DESCRIPTION",
        unit="micrometer",
        a_eln={"component": "NumberEditQuantity", "defaultDisplayUnit": "micrometer"},
    )


# this is not used yet
class SampleWithContacts(CompositeSystem, EntryData):
    """Class autogenerated from yaml schema."""

    m_def = Section(
        categories=[IKZHallCategory],
    )
    metal_stack = SubSection(section_def=MetalStack)


class ExperimentLakeshoreHall(Experiment, EntryData):
    """Class autogenerated from yaml schema."""

    m_def = Section(
        a_eln={"hide": ["steps"]},
        categories=[IKZHallCategory],
        label="Lakeshore Hall Experiment",
    )
    description = Quantity(
        type=str,
        description="description",
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
            label="Notes",
        ),
    )
    instrument = SubSection(
        section_def=HallInstrumentReference,
        repeats=True,
    )
    contacts_grafting = SubSection(section_def=ContactsGraftingReference, repeats=True)
    measurement = SubSection(section_def=HallMeasurementReference, repeats=True)


m_package.__init_metainfo__()
