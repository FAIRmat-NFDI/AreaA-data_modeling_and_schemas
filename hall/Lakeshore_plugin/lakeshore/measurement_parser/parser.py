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

from nomad.datamodel import EntryArchive
from nomad.metainfo import (
    MSection,
    Quantity,
)
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from lakeshore.schema import (
    HallExperiment,
    HallMeasurement,
    HallMeasurements
)

from nomad.datamodel.datamodel import (
    EntryArchive,
    EntryMetadata
)

from nomad.utils import hash
from nomad.parsing.tabular import (
    create_archive
)

class RawMeasurementFile(EntryData):
    measurement = Quantity(
        type=HallMeasurement,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class HallMeasurementsParser(MatchingParser):

    def __init__(self):
        super().__init__(
            name='NOMAD Lakeshore Hall measurements plugin',
            code_name= 'Lakeshore measurements Parser',
            code_homepage='https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas',
            supported_compressions=['gz', 'bz2', 'xz']
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        filetype = 'yaml'
        meas_file_name = f'{data_file[:-4]}_meas.archive.{filetype}'
        measurement_archive = EntryArchive(
            data=HallMeasurement(data_file=data_file_with_path),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id))
        archive.data = RawMeasurementFile(measurement=create_archive(measurement_archive.m_to_dict(), archive.m_context, meas_file_name, filetype, logger))
        archive.metadata.entry_name = data_file + ' measurement file'
        exp_file_name = f"{data_file[:-4]}_exp.archive.{filetype}"
        experiment_archive = EntryArchive(
            data=HallExperiment(measurement=[
                HallMeasurements(reference=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, meas_file_name)}#data')
                ]
                ),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id))
        create_archive(experiment_archive.m_to_dict(), archive.m_context, exp_file_name, filetype, logger)
