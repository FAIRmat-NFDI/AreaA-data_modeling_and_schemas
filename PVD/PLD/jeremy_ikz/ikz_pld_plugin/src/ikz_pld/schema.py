#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import re
import datetime

from typing import (
    Union,
    Dict,
    Any,
    TYPE_CHECKING,
)
from nomad_material_processing import (
    CrystallineSubstrate,
    ThinFilm,
    ThinFilmStack,
    Parallelepiped,
    SubstrateCrystalProperties,
    Miscut,
    Dopant,
)
from nomad_material_processing.physical_vapor_deposition import (
    PLDLaser,
    PLDSource,
    PVDChamberEnvironment,
    PVDPressure,
    PVDGasFlow,
    PVDSourcePower,
    PVDSubstrate,
    PVDSubstrateTemperature,
    PulsedLaserDeposition,
    PLDStep,
    PLDTarget,
    PLDTargetSource,
)
from nomad_material_processing.utils import (
    create_archive,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
    MProxy,
    Reference,
    SectionProxy,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    BrowserAnnotation,
    SectionProperties,
    ELNComponentEnum,
)
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    PureSubstanceComponent,
    PureSubstanceSection,
    PubChemPureSubstanceSection,
    ReadableIdentifiers,
    CompositeSystemReference,
)
from nomad.metainfo.metainfo import (
    Category,
)
from nomad.datamodel.data import (
    EntryDataCategory,
)
from nomad.datamodel.metainfo.workflow import (
    Link,
    Task,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name="IKZ PLD")


def read_dlog(file_path: str, logger: "BoundLogger" = None) -> Dict[str, Any]:
    """
    Function for reading the dlog of an IKZ PLD process.

    Args:
        file_path (str): The path to the PLD dlog file.
        logger (BoundLogger, optional): A structlog logger. Defaults to None.

    Returns:
        Dict[str, Any]: The flog data in a Python dictionary.
    """
    raise NotImplementedError


class IKZPLDCategory(EntryDataCategory):
    m_def = Category(
        label="IKZ Pulsed Laser Deposition", categories=[EntryDataCategory]
    )


class IKZPLDTarget(PLDTarget, EntryData):
    """
    A section for describing a target used for pulsed laser deposition at IKZ Berlin.
    """

    m_def = Section(
        categories=[IKZPLDCategory],
        label="Target",
    )
    recipe_name = Quantity(
        type=str,
        description="""
        The name of the target within the recipe.
        """,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
        ),
    )


class IKZPLDTargetReference(CompositeSystemReference):
    """
    A section used for referencing a CompositeSystem.
    """

    reference = Quantity(
        type=IKZPLDTarget,
        description="A reference to an IKZ PLD Target.",
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Target Reference",
        ),
    )


class IKZPLDPossibleSubstrate(CompositeSystem):
    pass


class IKZPLDSubstrate(CrystallineSubstrate, IKZPLDPossibleSubstrate, EntryData):
    m_def = Section(
        categories=[IKZPLDCategory],
        label="Substrate",
    )
    geometry = SubSection(
        section_def=Parallelepiped,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `IKZPLDSubstrate` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(IKZPLDSubstrate, self).normalize(archive, logger)


class IKZPLDSubstrateReference(ArchiveSection):
    substrate_number = Quantity(
        type=int,
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
        ),
    )
    substrate = Quantity(
        type=IKZPLDSubstrate,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
        ),
    )


class IKZPLDSubstrateSubBatch(ArchiveSection):
    name = Quantity(type=str)
    minimum_miscut_angle = Quantity(
        type=float,
        unit="degree",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
        ),
    )
    maximum_miscut_angle = Quantity(
        type=float,
        unit="degree",
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
        ),
    )
    amount = Quantity(
        type=int,
        description="""
        The number of substrates in this sub batch.
        """,
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
        ),
    )
    substrates = SubSection(
        section_def=IKZPLDSubstrateReference,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `IKZPLDSubstrateSubBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        if self.minimum_miscut_angle and self.maximum_miscut_angle:
            mean_angle = (
                self.maximum_miscut_angle.magnitude
                + self.minimum_miscut_angle.magnitude
            ) / 2
            self.name = f"{mean_angle:.3f}°"

        super(IKZPLDSubstrateSubBatch, self).normalize(archive, logger)


class IKZPLDSubstrateBatch(CompositeSystem, EntryData):  # TODO: Inherit from batch
    m_def = Section(
        categories=[IKZPLDCategory],
        label="Batch of Substrates",
        a_template={
            "geometry": {
                "height": 5e-4,
                "width": 5e-3,
                "length": 5e-3,
            },
        },
    )
    base_on = Quantity(
        type=Reference(SectionProxy("IKZPLDSubstrateBatch")),
        description="""
        Optional reference to another substrate batch that this batch is based on.
        """,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
            label="Base batch on",
        ),
    )
    material = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    miscut_orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    supplier_batch = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    supplier = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component="StringEditQuantity",
        ),
    )
    sub_batches = SubSection(
        section_def=IKZPLDSubstrateSubBatch,
        repeats=True,
    )
    geometry = SubSection(
        section_def=Parallelepiped,
    )
    dopants = SubSection(
        section_def=Dopant,
        repeats=True,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `IKZPLDSubstrateBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        if self.name is None and self.supplier_batch:
            self.name = self.supplier_batch
        if self.base_on is not None:
            self.material = self.base_on.material
            self.orientation = self.base_on.orientation
            self.miscut_orientation = self.base_on.miscut_orientation
            self.supplier_batch = self.base_on.supplier_batch
            self.sub_batches = self.base_on.sub_batches
            for sub_batch in self.sub_batches:
                sub_batch.substrates = []
            self.base_on = None
        elif len(self.sub_batches) > 0 and any(
            len(sub.substrates) == 0 for sub in self.sub_batches
        ):
            if self.material:
                substance_section = PubChemPureSubstanceSection(name=self.material)
                substance_section.normalize(archive, logger)
                self.components = [
                    PureSubstanceComponent(pure_substance=substance_section)
                ]
            for sub_batch_idx, sub_batch in enumerate(self.sub_batches):
                if len(sub_batch.substrates) > 0:
                    continue
                if self.supplier_batch:
                    batch_name = self.supplier_batch.replace("/", "-")
                else:
                    batch_name = f"batch-{datetime.datetime.now().isoformat()}"
                file_name = f"{batch_name}_sub-batch-%d_substrate-%d.archive.json"
                angle_deviation = (
                    sub_batch.maximum_miscut_angle.magnitude
                    - sub_batch.minimum_miscut_angle.magnitude
                ) / 2
                angle = sub_batch.minimum_miscut_angle.magnitude + angle_deviation
                sub_batch.substrates = [
                    IKZPLDSubstrateReference(
                        substrate_number=substrate_idx,
                        substrate=create_archive(
                            IKZPLDSubstrate(
                                name=f"{batch_name} {sub_batch.name} substrate-{substrate_idx}",
                                geometry=self.geometry,
                                crystal_properties=SubstrateCrystalProperties(
                                    orientation=self.orientation,
                                    miscut=Miscut(
                                        orientation=self.miscut_orientation,
                                        angle=angle,
                                        angle_deviation=angle_deviation,
                                    ),
                                ),
                                components=self.components,
                                supplier_id=self.supplier_batch,
                                supplier=self.supplier,
                                dopants=self.dopants,
                            ),
                            archive,
                            file_name % (sub_batch_idx, substrate_idx),
                        ),
                    )
                    for substrate_idx in range(sub_batch.amount)
                ]

        super(IKZPLDSubstrateBatch, self).normalize(archive, logger)


class IKZPLDSample(ThinFilmStack, IKZPLDPossibleSubstrate, EntryData):
    m_def = Section(
        categories=[IKZPLDCategory],
        label="Sample",
    )
    sample_id = SubSection(section_def=ReadableIdentifiers)


class IKZPLDLayerProcessConditions(ArchiveSection):
    """
    Process conditions for a layer in a pulsed laser deposition process at IKZ.
    """

    m_def = Section(
        categories=[IKZPLDCategory],
        label="Process Conditions",
    )
    growth_temperature = Quantity(
        type=float,
        unit="kelvin",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="celsius",
        ),
    )
    sample_to_target_distance = Quantity(
        type=float,
        unit="meter",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="millimeter",
        ),
    )
    pressure = Quantity(
        type=float,
        unit="pascal",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="mbar",
        ),
    )
    number_of_pulses = Quantity(
        type=float,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    laser_repetition_rate = Quantity(
        type=float,
        unit="hertz",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
        ),
    )
    laser_energy = Quantity(
        type=float,
        unit="joule",
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.NumberEditQuantity,
            defaultDisplayUnit="millijoule",
        ),
    )


class IKZPLDLayer(ThinFilm, EntryData):
    m_def = Section(
        categories=[IKZPLDCategory],
        label="Layer",
    )
    process_conditions = SubSection(
        section_def=IKZPLDLayerProcessConditions,
    )
    geometry = SubSection(
        section_def=Parallelepiped,
    )


class IKZPLDStep(PLDStep):
    """
    Application definition section for a step in a pulsed laser deposition process at IKZ.
    """

    m_def = Section(
        a_plot=[
            dict(
                label="Pressure and Temperature",
                x=[
                    "substrate/0/temperature/process_time",
                    "environment/pressure/process_time",
                ],
                y=[
                    "substrate/0/temperature/temperature",
                    "environment/pressure/pressure",
                ],
                lines=[
                    dict(
                        mode="lines",
                        line=dict(
                            color="rgb(25, 46, 135)",
                        ),
                    ),
                    dict(
                        mode="lines",
                        line=dict(
                            color="rgb(0, 138, 104)",
                        ),
                    ),
                ],
            ),
            dict(
                x="sources/0/evaporation_source/power/process_time",
                y="sources/0/evaporation_source/power/power",
            ),
            dict(
                x="substrate/0/temperature/process_time",
                y="substrate/0/temperature/temperature",
            ),
            dict(
                x="environment/pressure/process_time",
                y="environment/pressure/pressure",
            ),
        ],
    )
    sample_to_target_distance = Quantity(
        type=float,
        description="""
        The distance from the sample to the target.
        """,
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="millimeter",
        ),
        unit="meter",
    )

    def to_task(self) -> Task:
        """
        Returns the task description of this activity step.

        Returns:
            Task: The activity step as a workflow task.
        """
        outputs = []
        if self.substrate[0].thin_film is not None:
            outputs.append(
                Link(
                    name=self.substrate[0].thin_film.name,
                    section=self.substrate[0].thin_film,
                )
            )
        return Task(name=self.name, outputs=outputs)

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `IKZPLDStep` class. Will set the sample to target distance
        from the ELN field.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super(IKZPLDStep, self).normalize(archive, logger)
        if self.sample_to_target_distance is not None:
            for substrate in self.substrate:
                substrate.distance_to_source = [
                    self.sample_to_target_distance.to("meter").magnitude
                ]


def time_convert(x: Union[str, int]) -> int:
    """
    Help function for converting time stamps in log file to seconds.

    Args:
        x (Union[str, int]): The time in the format %h:%m:%s.

    Returns:
        int: The time in seconds.
    """
    if isinstance(x, int):
        return x
    h, m, s = map(int, x.split(":"))
    return (h * 60 + m) * 60 + s


class IKZPulsedLaserDeposition(PulsedLaserDeposition, EntryData):
    """
    Application definition section for a pulsed laser deposition process at IKZ.
    """

    m_def = Section(
        categories=[IKZPLDCategory],
        label="Pulsed Laser Deposition",
        links=["http://purl.obolibrary.org/obo/CHMO_0001363"],
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    "name",
                    "datetime",
                    "end_time",
                    "lab_id",
                    "attenuated_laser_energy",
                    "laser_spot_size",
                    "substrate",
                    "targets",
                    "data_log",
                    "recipe_log",
                    "steps",
                    "description",
                    "location",
                    "method",
                ],
            ),
            lane_width="800px",
        ),
        a_plot=[
            dict(
                x="steps/:/sources/:/evaporation_source/power/process_time",
                y="steps/:/sources/:/evaporation_source/power/power",
            ),
            dict(
                x="steps/:/substrate/:/temperature/process_time",
                y="steps/:/substrate/:/temperature/temperature",
            ),
            dict(
                x="steps/:/environment/pressure/process_time",
                y="steps/:/environment/pressure/pressure",
                layout=dict(
                    yaxis=dict(
                        type="log",
                    ),
                ),
            ),
        ],
    )
    substrate = Quantity(
        type=IKZPLDPossibleSubstrate,
        a_eln=ELNAnnotation(
            component="ReferenceEditQuantity",
        ),
    )
    targets = Quantity(
        type=IKZPLDTarget,
        shape=["*"],
        default=[],
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
        ),
    )
    attenuated_laser_energy = Quantity(
        type=float,
        unit="joule",
        default=50e-3,
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="millijoule",
        ),
    )
    laser_spot_size = Quantity(
        type=float,
        description="""
        The spot size of the laser on the target.
        """,
        a_eln=ELNAnnotation(
            component="NumberEditQuantity",
            defaultDisplayUnit="millimeter ** 2",
        ),
        unit="meter ** 2",
        default=3.6e-6,
    )
    data_log = Quantity(
        type=str,
        description="""
        The process log containing the data from all steps. (.dlog file).
        """,
        a_browser=BrowserAnnotation(adaptor="RawFileAdaptor"),
        a_eln=ELNAnnotation(
            component="FileEditQuantity",
            label="Data log (.dlog)",
        ),
    )
    recipe_log = Quantity(
        type=str,
        description="""
        The log detailing the steps. (.elog file).
        """,
        a_browser=BrowserAnnotation(adaptor="RawFileAdaptor"),
        a_eln=ELNAnnotation(
            component="FileEditQuantity",
            label="Data log (.elog)",
        ),
    )
    location = Quantity(
        type=str,
        description="""
        The location of the process in longitude, latitude.
        """,
        default="52.431685, 13.526855",
    )
    process_identifiers = SubSection(
        section_def=ReadableIdentifiers,
        description="""
        Sub section containing the identifiers used to generate the process ID.
        """,
    )

    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:
        """
        The normalizer for the `IKZPulsedLaserDeposition` class. Will generate and fill
        steps from the `.elog` and `.dlog` files.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        layers = {}
        if self.data_log and self.recipe_log:
            import pandas as pd
            import numpy as np
            from nomad.units import ureg

            pattern = re.compile(
                r"(?P<datetime>\d{8}_\d{4})-(?P<name>.+)\.(?P<type>d|e)log",
            )
            match = pattern.match(self.data_log)
            self.datetime = datetime.datetime.strptime(
                match["datetime"],
                r"%d%m%Y_%H%M",
            ).astimezone()
            self.name = match["name"]
            if self.process_identifiers is None:
                self.process_identifiers = ReadableIdentifiers(
                    institute="IKZ",
                    short_name=self.name,
                    datetime=self.datetime,
                )
                self.process_identifiers.normalize(archive, logger)
                self.lab_id = self.process_identifiers.lab_id

            with archive.m_context.raw_file(self.recipe_log, "r") as e_log:
                df_recipe = pd.read_csv(
                    e_log,
                    sep="\t",
                    names=["time_h", "process"],
                    header=None,
                )
            df_recipe = df_recipe[
                ~df_recipe["process"].str.contains("Abort Button pressed")
            ]
            df_recipe["time_s"] = df_recipe["time_h"].apply(time_convert)
            df_recipe["duration_s"] = df_recipe["time_s"].diff(-1) * -1
            df_steps = df_recipe.iloc[1:-1:3, :].copy()
            df_steps["pulses"] = (
                df_recipe.iloc[2:-1:3, 1].str.split().str[0].values.astype(int)
            )
            df_steps["recipe"] = df_steps["process"].str.split(":").str[1]
            self.end_time = self.datetime + datetime.timedelta(
                seconds=float(df_recipe.iloc[-1, 2]),
            )
            columns = [
                "time_s",
                "temperature_degc",
                "pressure2_mbar",
                "o2_flow_sccm",
                "n2_ar_flow_sccm",
                "frequency_hz",
                "laser_energy_mj",
                "pressure1_mbar",
                "zeros",
            ]
            with archive.m_context.raw_file(self.data_log, "r") as d_log:
                df_data = pd.read_csv(
                    d_log,
                    sep="\t",
                    names=columns,
                )
            substrate_ref = None
            sample_id = None
            if isinstance(self.substrate, MProxy):
                self.substrate.m_proxy_resolve()
            if isinstance(self.substrate, IKZPLDSubstrate):
                sample_id = f"{self.lab_id}-PLD-Sample"
                substrate_ref = self.substrate
            elif isinstance(self.substrate, IKZPLDSample):
                sample_id = self.substrate.sample_id.lab_id
                substrate_ref = self.substrate.substrate
            steps = []
            target_recipe_names = [target.recipe_name for target in self.targets]
            if len(self.steps) == len(df_steps):
                target_distances = [
                    step.sample_to_target_distance for step in self.steps
                ]
            else:
                target_distances = [None] * len(df_steps)
            for target_distance, (_, row) in zip(target_distances, df_steps.iterrows()):
                if target_distance is not None:
                    target_distance = target_distance.to("meter").magnitude
                step_pattern = re.compile(
                    r"^(?P<step>[a-z]*?)(?P<target>[A-Z]*)(?P<temp>\d*)$"
                )
                step_match = step_pattern.match(row["recipe"])
                target = None
                try:
                    target = self.targets[
                        target_recipe_names.index(step_match["target"])
                    ]
                except ValueError:
                    logger.warning(
                        f'Target {step_match["target"]} not found in target list.'
                    )
                    target = None
                data = df_data.loc[
                    (row["time_s"] <= df_data["time_s"])
                    & (df_data["time_s"] < (row["time_s"] + row["duration_s"]))
                ].copy()
                data["pressure_mbar"] = data["pressure1_mbar"]
                p2_range = (0.01 <= data["pressure_mbar"]) & (
                    data["pressure_mbar"] <= 0.1
                )
                data.loc[p2_range, "pressure_mbar"] = data.loc[
                    p2_range, "pressure2_mbar"
                ]
                mean_laser_energy = data["laser_energy_mj"].replace(0, np.NaN).mean()
                if np.isnan(mean_laser_energy):
                    attenuation = 1
                else:
                    attenuation = self.attenuated_laser_energy / (
                        mean_laser_energy * 1e-3
                    )
                creates_new_thin_film = row["pulses"] > 0
                evaporation_source = PLDLaser(
                    power=PVDSourcePower(
                        power=(
                            data["laser_energy_mj"]
                            * 1e-3
                            * data["frequency_hz"]
                            * attenuation
                        ),
                        process_time=data["time_s"],
                    ),
                    wavelength=248e-9,
                    repetition_rate=data["frequency_hz"].mean(),
                    spot_size=self.laser_spot_size.magnitude,
                    pulses=row["pulses"],
                )
                target_source = PLDTargetSource(
                    material=target,
                )
                source = PLDSource(
                    evaporation_source=evaporation_source,
                    material_source=target_source,
                )
                environment = PVDChamberEnvironment(
                    pressure=PVDPressure(
                        pressure=data["pressure_mbar"],
                        process_time=data["time_s"],
                    ),
                    gas_flow=[
                        PVDGasFlow(
                            gas=PubChemPureSubstanceSection(name="Oxygen"),
                            flow=ureg.Quantity(
                                data["o2_flow_sccm"].values, ureg("cm ** 3 / minute")
                            )
                            .to("meter ** 3 / second")
                            .magnitude,
                            process_time=data["time_s"],
                        ),
                        PVDGasFlow(
                            gas=PureSubstanceSection(name="Argon/Nitrogen"),
                            flow=ureg.Quantity(
                                data["n2_ar_flow_sccm"].values, ureg("cm ** 3 / minute")
                            )
                            .to("meter ** 3 / second")
                            .magnitude,
                            process_time=data["time_s"],
                        ),
                    ],
                )
                thin_film = None
                if (
                    creates_new_thin_film
                    and target_distance is not None
                    and sample_id is not None
                ):
                    layer_count = len(layers) + 1
                    layer_id = f"{sample_id}-L{layer_count}"
                    elemental_composition = []
                    if target is not None:
                        elemental_composition = target.elemental_composition
                    if substrate_ref is not None and substrate_ref.geometry is not None:
                        geometry = Parallelepiped()
                        geometry.width = substrate_ref.geometry.width
                        geometry.length = substrate_ref.geometry.length
                    else:
                        geometry = None
                    name = f"{sample_id} Layer {layer_count}"
                    thin_film = create_archive(
                        entity=IKZPLDLayer(
                            name=name,
                            elemental_composition=elemental_composition,
                            process_conditions=IKZPLDLayerProcessConditions(
                                growth_temperature=data["temperature_degc"].mean()
                                + 273.15,
                                pressure=ureg.Quantity(
                                    data["pressure_mbar"].mean(), ureg("mbar")
                                )
                                .to("pascal")
                                .magnitude,
                                sample_to_target_distance=target_distance,
                                number_of_pulses=row["pulses"],
                                laser_repetition_rate=data["frequency_hz"].mean(),
                                laser_energy=self.attenuated_laser_energy.to(
                                    "joule"
                                ).magnitude,
                            ),
                            geometry=geometry,
                        ),
                        archive=archive,
                        file_name=f"{layer_id}.archive.json",
                    )
                    layers[name] = thin_film
                substrate = PVDSubstrate(
                    temperature=PVDSubstrateTemperature(
                        temperature=data["temperature_degc"] + 273.15,
                        process_time=data["time_s"],
                        measurement_type="Heater thermocouple",
                    ),
                    heater="Resistive element",
                    thin_film=thin_film,
                )
                step = IKZPLDStep(
                    name=row["recipe"],
                    creates_new_thin_film=creates_new_thin_film,
                    sample_to_target_distance=target_distance,
                    duration=row["duration_s"],
                    sources=[source],
                    substrate=[substrate],
                    environment=environment,
                )
                step.normalize(archive, logger)
                steps.append(step)
            self.steps = steps

            if isinstance(self.substrate, IKZPLDSubstrate) and len(layers) > 0:
                self.samples = [
                    CompositeSystemReference(
                        name=sample_id,
                        reference=create_archive(
                            entity=IKZPLDSample(
                                substrate=self.substrate.m_proxy_value,
                                lab_id=sample_id,
                                layers=[layer for layer in layers.values()],
                            ),
                            archive=archive,
                            file_name=f"{sample_id}.archive.json",
                        ),
                    )
                ]
            elif isinstance(self.substrate, IKZPLDSample) and len(steps) > 0:
                self.samples = [
                    CompositeSystemReference(
                        name=sample_id,
                        reference=self.substrate,
                    )
                ]
            if len(self.samples) > 0:
                for step in self.steps:
                    step.substrate[0].substrate = self.samples[0].reference

        archive.workflow2 = None
        super(IKZPulsedLaserDeposition, self).normalize(archive, logger)
        if self.substrate is not None:
            archive.workflow2.inputs.append(
                Link(name=f"Substrate: {self.substrate.name}", section=self.substrate)
            )
        for target in self.targets:
            archive.workflow2.inputs.append(
                Link(name=f"Target: {target.name}", section=target)
            )
        for name, layer in layers.items():
            archive.workflow2.outputs.append(Link(name=f"Layer: {name}", section=layer))


m_package.__init_metainfo__()
