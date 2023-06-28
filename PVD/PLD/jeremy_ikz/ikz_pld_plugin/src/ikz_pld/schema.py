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

from typing import Union
from nomad_material_processing import (
    Substrate,
    ThinFilmStack,
)
from nomad_material_processing.physical_vapor_deposition import (
    PLDLaser,
    PLDSource,
    PVDChamberEnvironment,
    PVDPressure,
    PVDSourcePower,
    PVDSubstrate,
    PVDSubstrateTemperature,
    PulsedLaserDeposition,
    PLDStep,
)
from nomad_material_processing.utils import (
    create_archive,
)
from structlog.stdlib import (
    BoundLogger,
)
from nomad.units import (
    ureg,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    BrowserAnnotation,
    SectionProperties,
)
from nomad.datamodel.metainfo.eln import (
    SampleID,
    Substance,
    Component,
    Ensemble,
)

m_package = Package(name='IKZ PLD')


class IKZPLDSubstrateMaterial(Substance, EntryData):
    pass


class IKZPLDPossibleSubstrate(Ensemble):
    pass


class IKZPLDSubstrate(Substrate, IKZPLDPossibleSubstrate, EntryData):
    material=Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    miscut_orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    minimum_miscut_angle = Quantity(
        type=float,
        unit='degree',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    maximum_miscut_angle = Quantity(
        type=float,
        unit='degree',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    supplier_batch = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `IKZPLDSubstrate` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        if self.material and len(self.components) == 0:
            substance = IKZPLDSubstrateMaterial(
                name=self.material,
            )
            file_name = f'{datetime.datetime.now().isoformat()}_substance.archive.json'
            self.components = [Component(
                system=create_archive(substance, archive, file_name),
            )]
        super(IKZPLDSubstrate, self).normalize(archive, logger)


class IKZPLDSubstrateReference(ArchiveSection):
    substrate_number = Quantity(
        type=int,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    substrate = Quantity(
        type=IKZPLDSubstrate,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class IKZPLDSubstrateSubBatch(ArchiveSection):
    name = Quantity(
        type=str
    )
    minimum_miscut_angle = Quantity(
        type=float,
        unit='degree',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    maximum_miscut_angle = Quantity(
        type=float,
        unit='degree',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    amount = Quantity(
        type=int,
        description='''
        The number of substrates in this sub batch.
        ''',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
        ),
    )
    substrates = SubSection(
        section_def=IKZPLDSubstrateReference,
        repeats=True,
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `IKZPLDSubstrateSubBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        if self.name is None and self.minimum_miscut_angle and self.maximum_miscut_angle:
            mean_angle = (self.maximum_miscut_angle.magnitude + self.minimum_miscut_angle.magnitude) / 2
            self.name = f'{mean_angle}°'

        super(IKZPLDSubstrateSubBatch, self).normalize(archive, logger)


class IKZPLDSubstrateBatch(Ensemble, EntryData):  # TODO: Inherit from batch
    material=Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    miscut_orientation = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    supplier_batch = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    sub_batches = SubSection(
        section_def=IKZPLDSubstrateSubBatch,
        repeats=True,
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `IKZPLDSubstrateBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        if self.name is None and self.supplier_batch:
            self.name = self.supplier_batch
        if (
            len(self.sub_batches) > 0
            and any(len(sub.substrates) == 0 for sub in self.sub_batches)
        ):
            substance_ref = None
            if self.material:
                substance = IKZPLDSubstrateMaterial(
                    name=self.material,
                )
                file_name = f'{datetime.datetime.now().isoformat()}_substance.archive.json'
                substance_ref = create_archive(substance, archive, file_name)
                self.components = [Component(system=substance_ref)]
            for sub_batch_idx, sub_batch in enumerate(self.sub_batches):
                if len(sub_batch.substrates) > 0:
                    continue
                if self.supplier_batch:
                    batch_name = self.supplier_batch.replace('/','-')
                else:
                    batch_name = f'batch-{datetime.datetime.now().isoformat()}'
                file_name = f'{batch_name}_sub-batch-%d_substrate-%d.archive.json'
                sub_batch.substrates = [
                    IKZPLDSubstrateReference(
                        substrate_number=substrate_idx,
                        substrate=create_archive(
                            IKZPLDSubstrate(
                                name=f'{batch_name} {sub_batch.name} substrate-{substrate_idx}',
                                material=self.material,
                                orientation=self.orientation,
                                miscut_orientation=self.miscut_orientation,
                                supplier_batch=self.supplier_batch,
                                minimum_miscut_angle=sub_batch.minimum_miscut_angle.magnitude,
                                maximum_miscut_angle=sub_batch.maximum_miscut_angle.magnitude,
                                components=[Component(system=substance_ref)],
                            ),
                            archive,
                            file_name % (sub_batch_idx, substrate_idx),
                        )
                    ) for substrate_idx in range(sub_batch.amount)
                ]

        super(IKZPLDSubstrateBatch, self).normalize(archive, logger)


class IKZPLDSample(ThinFilmStack, IKZPLDPossibleSubstrate, EntryData):
    sample_id = SubSection(
        section_def=SampleID
    )


class IKZPLDStep(PLDStep):
    '''
    Application definition section for a step in a pulsed laser deposition process at IKZ.
    '''
    m_def = Section(
        a_plot=[
            dict(
                label='Pressure and Temperature',
                x=[
                    'substrate/0/temperature/process_time',
                    'environment/pressure/process_time',
                ],
                y=[
                    'substrate/0/temperature/temperature',
                    'environment/pressure/pressure',
                ],
                lines=[
                    dict(
                        mode= 'lines',
                        line=dict(
                            color='rgb(25, 46, 135)',
                        ),
                    ),
                    dict(
                        mode= 'lines',
                        line=dict(
                            color='rgb(0, 138, 104)',
                        ),
                    ),
                ]
            ),
            dict(
                x='sources/0/evaporation_source/power/process_time',
                y='sources/0/evaporation_source/power/power',
            ),
            dict(
                x='substrate/0/temperature/process_time',
                y='substrate/0/temperature/temperature',
            ),
            dict(
                x='environment/pressure/process_time',
                y='environment/pressure/pressure',
            ),
        ],
    )
    sample_to_target_distance = Quantity(
        type=float,
        description='''
        The distance from the sample to the target.
        ''',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='meter',
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `IKZPLDStep` class. Will set the sample to target distance
        from the ELN field.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(IKZPLDStep, self).normalize(archive, logger)
        self.substrate.distance_to_source = [self.sample_to_target_distance]


def time_convert(x: Union[str, int])-> int:
    '''
    Help function for converting time stamps in log file to seconds.

    Args:
        x (Union[str, int]): The time in the format %h:%m:%s.

    Returns:
        int: The time in seconds.
    '''
    if isinstance(x, int):
        return x
    h,m,s = map(int,x.split(':'))
    return (h*60+m)*60+s


class IKZPulsedLaserDeposition(PulsedLaserDeposition, EntryData):
    '''
    Application definition section for a pulsed laser deposition process at IKZ.
    '''
    m_def = Section(
        links=['http://purl.obolibrary.org/obo/CHMO_0001363'],
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'datetime',
                    'end_time',
                    'lab_id',
                    'attenuated_laser_energy',
                    'laser_spot_size',
                    'data_log',
                    'recipe_log',
                    'steps',
                    'description',
                    'location',
                    'method',
                ],
            ),
            lane_width='800px',
        ),
        a_plot=[
            dict(
                x='steps/:/sources/:/evaporation_source/power/process_time',
                y='steps/:/sources/:/evaporation_source/power/power',
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
    substrate = Quantity(
        type=IKZPLDPossibleSubstrate,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )
    attenuated_laser_energy = Quantity(
        type=float,
        unit='joule',
        default=50e-3,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millijoule',
        ),
    )
    laser_spot_size = Quantity(
        type=float,
        description='''
        The spot size of the laser on the target.
        ''',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter ** 2',
        ),
        unit='meter ** 2',
        default=3.6e-6,
    )
    data_log = Quantity(
        type=str,
        description='''
        The process log containing the data from all steps. (.dlog file).
        ''',
        a_browser=BrowserAnnotation(
            adaptor='RawFileAdaptor'
        ),
        a_eln=ELNAnnotation(
            component='FileEditQuantity'
        ),
    )
    recipe_log = Quantity(
        type=str,
        description='''
        The log detailing the steps. (.elog file).
        ''',
        a_browser=BrowserAnnotation(
            adaptor='RawFileAdaptor'
        ),
        a_eln=ELNAnnotation(
            component='FileEditQuantity'
        ),
    )
    location = Quantity(
        type=str,
        description='''
        The location of the process in longitude, latitude.
        ''',
        default='52.431685, 13.526855',
    )
    process_identifiers = SubSection(
        section_def=SampleID,
        description='''
        Sub section containing the identifiers used to generate the process ID.
        ''',
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        '''
        The normalizer for the `IKZPulsedLaserDeposition` class. Will generate and fill
        steps from the `.elog` and `.dlog` files.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        '''
        super(IKZPulsedLaserDeposition, self).normalize(archive, logger)
        if self.data_log and self.recipe_log:
            import pandas as pd
            import numpy as np

            # If no substrate is already added
            # if not any(sub.substrate is not None for step in self.steps for sub in step.substrate):
            substrate_ref = None
            if (
                len(self.steps) > 0
                and self.steps[0].substrate is not None
                and self.steps[0].substrate.substrate is not None
            ):
                substrate_ref = self.steps[0].substrate.substrate
            elif isinstance(self.substrate, IKZPLDSubstrate):
                substrate_ref = create_archive(
                    IKZPLDSample(
                        substrate=self.substrate,
                    )
                )
            elif isinstance(self.substrate, IKZPLDSample):
                substrate_ref = self.substrate
            pattern = re.compile(
                r'(?P<datetime>\d{8}_\d{4})-(?P<name>.+)\.(?P<type>d|e)log',
            )
            match = pattern.match(self.data_log)
            self.datetime = datetime.datetime.strptime(
                match['datetime'],
                r'%d%m%Y_%H%M',
            ).astimezone()
            self.name = match['name']
            self.process_identifiers = SampleID(
                sample_short_name=self.name,
                creation_datetime=self.datetime,
            )
            self.process_identifiers.normalize(archive, logger)
            self.lab_id = self.process_identifiers.sample_id
            with archive.m_context.raw_file(self.recipe_log, 'r') as e_log:
                df_recipe = pd.read_csv(
                    e_log,
                    sep='\t',
                    names=['time_h','process'],
                    header=None,
                )
            df_recipe['time_s'] = df_recipe['time_h'].apply(time_convert)
            df_recipe['duration_s'] = df_recipe['time_s'].diff(-1) * -1
            df_steps = df_recipe.iloc[1:-1:3,:].copy()
            df_steps['pulses'] = df_recipe.iloc[2:-1:3,1].str.split().str[0].values.astype(int)
            df_steps['recipe'] = df_steps['process'].str.split(':').str[1]
            self.end_time = self.datetime + datetime.timedelta(
                seconds=float(df_recipe.iloc[-1,2]),
            )
            columns = [
                'time_s',
                'temperature_degc',
                'pressure2_mbar',
                'o2_flow_sccm',
                'n2_ar_flow_sccm',
                'frequency_hz',
                'laser_energy_mj',
                'pressure1_mbar',
                'zeros',
            ]
            with archive.m_context.raw_file(self.data_log, 'r') as d_log:
                df_data = pd.read_csv(
                    d_log,
                    sep='\t',
                    names=columns,
                )

            steps = []
            for _, row in df_steps.iterrows():
                data = df_data.loc[
                    (row['time_s'] <= df_data['time_s']) &
                    (df_data['time_s'] < (row['time_s'] + row['duration_s']))
                ].copy()
                data['pressure_mbar'] = data['pressure1_mbar']
                p2_range = (0.01 <= data['pressure_mbar']) & (data['pressure_mbar'] <= 0.1)
                data.loc[p2_range, 'pressure_mbar'] = data.loc[p2_range, 'pressure2_mbar']
                mean_laser_energy = data['laser_energy_mj'].replace(0, np.NaN).mean()
                if np.isnan(mean_laser_energy):
                    attenuation = 1
                else:
                    attenuation = self.attenuated_laser_energy / (mean_laser_energy * 1e-3)
                evaporation_source = PLDLaser(
                    power=PVDSourcePower(
                        power=(
                            data['laser_energy_mj'] * 1e-3 * data['frequency_hz']
                            * attenuation
                        ),
                        process_time=data['time_s']
                    ),
                    wavelength=248e-9,
                    repetition_rate=data['frequency_hz'].mean(),
                    spot_size=self.laser_spot_size.magnitude,
                    pulses=row['pulses'],
                )
                source = PLDSource(
                    evaporation_source=evaporation_source,
                )
                substrate = PVDSubstrate(
                    temperature=PVDSubstrateTemperature(
                        temperature=data['temperature_degc'] + 273.15,
                        process_time=data['time_s'],
                        measurement_type='Heater thermocouple',
                    ),
                    heater='Resistive element',
                    substrate=substrate_ref,
                )
                environment = PVDChamberEnvironment(
                    pressure=PVDPressure(
                        pressure=data['pressure_mbar'],
                        process_time=data['time_s'],
                    )
                )
                step = IKZPLDStep(
                    name=row['recipe'],
                    creates_new_thin_film=row['pulses'] > 0,
                    duration=row['duration_s'],
                    sources=[source],
                    substrate=[substrate],
                    environment=environment,
                )
                steps.append(step)
            self.steps = steps


m_package.__init_metainfo__()
