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

'''
Defines the schema for the ELN where the data from data files is parsed into.
It also defines functions to generate a Jupyter notebook based on the data.
ELN is generated when a data file is dropped to create an entry and matched by the
parser. Alternately, one can create an empty ELN and add a data file on the go.
ELN can also search for a data file from the previous uploads. It populates the fields
based on the associated schemas for the data file type.

The schema support one data file per ELN. This data file could can have any data format.
Normalizing this ELN will generate a Jupyter notebook with containing a filepath to the
data file. In case the file type is supported by the parser, for example supported XRD
files, the Jupyter notebook will contain the parsed data.

Eventually, the schema will support multiple data files per ELN and support parsing of
file types from other measurements and processes.
'''
from typing import (
    TYPE_CHECKING
)
from nomad.datamodel.metainfo.basesections import (
    Analysis,
    AnalysisResult,
)
from nomad.metainfo import (
    Package,
    Section,
    Quantity,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name = 'analysis_jupyter')

def generate_jupyter_notebook(archive: 'EntryArchive', logger: 'BoundLogger'):
    '''
    TODO: Generates a Jupyter notebook from the ELN.
    generating the notebook based on the file type
    perform a check to see if jupyter notebook with same content is already present
    as the normalize would be needed again to fill in the output results section
    getting the results from the analysis back into the ELN
    '''

def get_input_files(archive: 'EntryArchive', logger: 'BoundLogger') -> list:
    '''
    Finds the analysis input files from the current upload.

    Args:
        archive (EntryArchive): The archive containing the section.
        logger (BoundLogger): A structlog logger.

    Returns:
        list: List containing matching input files.
    '''
    from nomad.search import search

    # TODO: support more sections
    section_lookup = [
        'ELNXRayDiffraction',
    ]

    result = search(
        owner = 'user',
        query = {
            'results.eln.sections:any' : section_lookup,
            'upload_id:any' : [archive.m_context.upload_id],
        },
        user_id = archive.metadata.main_author.user_id,
    )
    if not result.data:
        logger.warning('No matching input files found in the uploads')

    return result.data

class JupyterAnalysisResult(AnalysisResult):
    '''
    Section for collecting Jupyter notebook analysis results.
    It is a non-editable section that is populated once the processing is.
    '''
    m_def = Section()
    analysis_status = Quantity(
        type=bool,
        description='Status of the Jupyter notebook generation and analysis',
        a_eln = ELNAnnotation(
            label = 'Analysis Status',
            component = None,
        ),
    )

class JupyterAnalysis(Analysis):
    '''
    Generic class for Jupyter notebook analysis.
    '''
    m_def = Section()

class ELNJupyterAnalysis(JupyterAnalysis, EntryData):
    '''
    Entry section for Jupyter notebook analysis.
    '''
    m_def = Section(
        category = None,
        label = 'Jupyter Notebook Analysis',
    )
    input_file = Quantity(
        type=str,
        description='Input file (raw data file or parsed archive)',
        a_eln = ELNAnnotation(
            component = ELNComponentEnum.FileEditQuantity,
        ),
    )
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        '''
        Normalizes the ELN entry to generate a Jupyter notebook.
        '''
        super().normalize(archive, logger)

        input_files = get_input_files(archive, logger)
        if len(input_files) > 1:
            logger.warning((
                'Multiple input files found.'
                f'Using the first one "{input_files[0].get("entry_name")}".'
            ))
            input_files = input_files[:1]

        generate_jupyter_notebook(archive, logger)

m_package.__init_metainfo__()
