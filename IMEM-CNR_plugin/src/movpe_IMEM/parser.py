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
from time import (
    sleep,
    perf_counter
)
import pandas as pd
import datetime

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
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad_material_processing.utils import create_archive as create_archive_ref
from nomad.parsing.tabular import create_archive
from nomad.search import search
from movpe_IMEM import (
    MovpeIMEMExperiment,
    GrowthRuns,
    GrowthRun,
    GrownSamples,
    GrownSample,
    HallMeasurements,
    HallMeasurement,
    HallMeasurementResult
)

from nomad.utils import hash


class GrowthFile(EntryData):
    experiment = Quantity(
        type=MovpeIMEMExperiment,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        )
    )


class MovpeIMEMParser(MatchingParser):

    def __init__(self):
        super().__init__(
            name='NOMAD movpe IMEM-CNR schema and parser plugin',
            code_name= 'movpe IMEM-CNR Parser',
            code_homepage='https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas',
            supported_compressions=['gz', 'bz2', 'xz']
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        xlsx = pd.ExcelFile(mainfile)
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split("raw/")[-1]
        sheet = pd.read_excel(xlsx, 'Overview', comment="#", converters={'Sample':str})
        growth_run_sheet = sheet.rename(columns=lambda x: x.strip())
        grown_sample_id = growth_run_sheet["Sample"][0]
        filetype = "yaml"
        grown_sample_filename = f"{grown_sample_id}_grownsample.archive.{filetype}"
        grown_sample_archive = EntryArchive(
            data=GrownSample(lab_id=grown_sample_id),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        create_archive(
            grown_sample_archive.m_to_dict(),
            archive.m_context,
            grown_sample_filename,
            filetype,
            logger,
        )

        tic = perf_counter()
        while True:
            search_result = search(
                owner="all",
                query={"results.eln.lab_ids:any": [grown_sample_id]},
                user_id=archive.metadata.main_author.user_id,
            )
            # checking if the grown sample entries are properly indexed
            if search_result.pagination.total == 1:
                break
            if search_result.pagination.total > 1:
                matches = []
                for match in search_result.data:
                    matches.append(match['results']['eln']['lab_ids'])
                logger.warning(f'Some entries with lab_id {matches} are duplicated')
                break
            # otherwise wait until all are indexed
            sleep(0.1)
            toc = perf_counter()
            if toc - tic > 15:
                logger.warning(f"The entry with lab_id {grown_sample_id} was not found and couldn't be referenced.")
                break

        sheet = pd.read_excel(xlsx, 'ElectroOptical', comment="#", converters={'Sample':str})
        hall_measurement_sheet = sheet.rename(columns=lambda x: x.strip())
        hall_meas_refs = []
        for meas_index, hall_measurement in hall_measurement_sheet.iterrows():
            filetype = "yaml"
            hall_meas_filename = f"{hall_measurement['Sample']}_{meas_index}_hall.archive.{filetype}"
            hall_meas_archive = EntryArchive(
                data=HallMeasurement(
                    lab_id=hall_measurement['Sample'],
                    datetime=datetime.datetime.strptime(hall_measurement['Date'],r'%Y-%m-%d').astimezone(),
                    results=[
                        HallMeasurementResult(
                            resistivity=hall_measurement['Resistivity'],
                            mobility=hall_measurement['Mobility'],
                            carrier_concentration=hall_measurement['Carrier Concentration'],
                        )
                    ]
                ),
                m_context=archive.m_context,
                metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
            )
            create_archive(
                hall_meas_archive.m_to_dict(),
                archive.m_context,
                hall_meas_filename,
                filetype,
                logger,
            )
            hall_meas_refs.append(
                HallMeasurements(
                    reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, hall_meas_filename)}#data")
                    )

        growth_run_entry = GrowthRun(
            data_file=data_file_with_path
        )
        growth_run_filename = f'{growth_run_sheet["Sample"][0]}_growthrun.archive.json'

        entry = MovpeIMEMExperiment(
            data_file=data_file_with_path,
            growth_run=GrowthRuns(
                reference=create_archive_ref(growth_run_entry,archive,growth_run_filename)
            ),
            grown_samples=[
                GrownSamples(
                    reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, grown_sample_filename)}#data")
            ],
            hall_measurement=hall_meas_refs,
            date=growth_run_sheet["Date"][0],
            film=growth_run_sheet["Film"][0],
            carrier_gas=growth_run_sheet["Carrier Gas"][0],
            VI_III_ratio=growth_run_sheet["VI III Ratio"][0],
            growth_time=growth_run_sheet["Growth Time"][0]
            )
        experiment_file_name = f'{data_file[:-5]}.archive.json'
        archive.data = GrowthFile(experiment=create_archive_ref(entry,archive,experiment_file_name))
        archive.metadata.entry_name = data_file + ' experiment file'