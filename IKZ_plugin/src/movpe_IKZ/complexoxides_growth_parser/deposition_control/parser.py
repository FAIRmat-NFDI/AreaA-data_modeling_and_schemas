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
from nomad.search import search
from nomad_material_processing.utils import create_archive as create_archive_ref
from movpe_IKZ import (
    MovpeComplexOxidesIKZExperiment,
    ComplexOxideGrowths,
    ComplexOxideGrowth,
    GrownSample
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing.tabular import create_archive
from nomad.utils import hash


class RawFile(EntryData):
    constant_parameters_file = Quantity(
        type=ComplexOxideGrowth,
        # a_eln=ELNAnnotation(
        #     component="ReferenceEditQuantity",
        # ),
        #shape=['*']
    )


class MovpeDepositionControlIKZParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name="NOMAD complex oxides growth movpe IKZ schema and parser plugin",
            code_name="complex oxides growth movpe IKZ parser",
            code_homepage="https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas",
            supported_compressions=["gz", "bz2", "xz"],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        xlsx = pd.ExcelFile(mainfile)
        data_file = mainfile.split("/")[-1]
        overview = pd.read_excel(xlsx, 'Overview', comment="#", converters={'Overview':str})
        if len(overview["Activity ID"]) > 1:
            logger.warning(f"Only one line expected in the Overview sheet of {data_file}")
        filetype = "yaml"
        filename = f"{overview['Activity ID'][0]}_constant_parameters_growth.archive.{filetype}"
        growth_archive = EntryArchive(
            data=ComplexOxideGrowth(lab_id=overview["Activity ID"][0]),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        create_archive(
            growth_archive.m_to_dict(),
            archive.m_context,
            filename,
            filetype,
            logger,
        )
        archive.data = RawFile(
            constant_parameters_file=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, filename)}#data"
        )
        archive.metadata.entry_name = overview["Activity ID"][0] + "constant parameters file"

