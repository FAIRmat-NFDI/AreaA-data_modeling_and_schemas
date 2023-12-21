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
    SectionReference,
)
from nomad.metainfo import (
    Package,
    Section,
    Quantity,
    SubSection,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    BrowserAnnotation,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name = 'analysis_jupyter')

def get_input_entry_ids(archive: 'EntryArchive', logger: 'BoundLogger') -> list:
    '''
    Finds the analysis input files from the current upload and returns the entry_id.

    Args:
        archive (EntryArchive): The archive containing the section.
        logger (BoundLogger): A structlog logger.

    Returns:
        list: List containing matching entry_ids.
    '''
    from nomad.search import search
    from nomad.app.v1.models import MetadataRequired

    result = search(
        owner = 'user',
        query = {
            'results.eln.sections:any' : ['EntryData'],
            'upload_id' : [archive.m_context.upload_id],
        },
        required = MetadataRequired(include=['entry_id']),
        user_id = archive.metadata.main_author.user_id,
    )
    if not result.data:
        logger.warning('No EntryData section found in the upload.')

    entry_ids = [data['entry_id'] for data in result.data]
    return entry_ids


class JupyterAnalysisResult(AnalysisResult):
    '''
    Section for collecting Jupyter notebook analysis results.
    It is a non-editable section that is populated once the processing is.
    '''
    connection_status = Quantity(
        type = str,
        default = 'Not connected',
        description = 'Status of connection with Jupyter notebook',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        '''
        The normalize function for `JupyterAnalysisResult` section.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        super().normalize(archive, logger)

class JupyterAnalysis(Analysis):
    '''
    Generic class for Jupyter notebook analysis.
    '''
    m_def = Section()
    inputs = SubSection(
        section_def = SectionReference,
        description = 'The input sections for the analysis',
        repeats = True,
    )
    outputs = SubSection(
        section_def = JupyterAnalysisResult,
        description = 'The output sections for the analysis',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        '''
        The normalize function for `JupyterAnalysis` section.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        super().normalize(archive, logger)

class ELNJupyterAnalysis(JupyterAnalysis, EntryData):
    '''
    Entry section for Jupyter notebook analysis.
    '''
    m_def = Section(
        # TODO: add category when shifted to a specific plugin
        category = None,
        label = 'Jupyter Notebook Analysis',
    )
    notebook = Quantity(
        type=str,
        description='Generated Jupyter notebook file',
        a_eln = ELNAnnotation(
            label = 'Jupyter Notebook',
            component = ELNComponentEnum.FileEditQuantity,
        ),
        a_browser = BrowserAnnotation(
            adaptor = 'RawFileAdaptor'
        )
    )


    def link_jupyter_notebook(self,path) -> None:
        self.notebook = path

    def write_jupyter_notebook(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        Writes (or overwrites) a Jupyter notebook and saves it as a raw file.

        Args:
            archive (EntryArchive): The archive containing the section.
            input_file_ids (list): List of input file ids.
            logger (BoundLogger): A structlog logger.
        '''

        # TODO:  add analysis code specific to the section type to which the entry belongs

        entry_ids = []
        if self.inputs is not None:
            for entry in self.inputs:
                entry_ids.append(entry.reference.m_parent.entry_id)

        if len(entry_ids) == 0:
            logger.warning('No EntryArchive linked.')

        try:
            import nbformat as nbf

            file_name = 'ELNJupyterAnalysis.ipynb'

            cells = []

            code = (
            'import requests\n'
            'from nomad.client import Auth'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            code = (
            'base_url = "http://nomad-lab.eu/prod/v1/api/v1"\n'
            'token_header = Auth().headers()'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            code = (
            'def get_entry_data(entry_id):\n'
            '   query = {\n'
            '       "required" : {\n'
            '           "data": "*",\n'
            '       }\n'
            '   }\n'
            '   response = requests.post(\n'
            '       f"{base_url}/entries/{entry_id}/archive/query",\n'
            '       headers = token_header,\n'
            '       json = query\n'
            '   )\n'
            '   return response.json()\n'
            'entry_data = []\n'
            f'for entry_id in {entry_ids}:\n'
            '   entry_data.append(get_entry_data(entry_id))'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            code = (
            'print(f"Data from {len(entry_data)} entries is available in `entry_data: list` variable.\\n")\n'
            'print(entry_data)'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            nb = nbf.v4.new_notebook()
            for cell in cells:
                nb.cells.append(cell)

            with archive.m_context.raw_file(file_name, 'w') as nb_file:
                nbf.write(nb, nb_file)
            archive.m_context.process_updated_raw_file(file_name, allow_modify=True)

        except Exception as e:
            logger.error(f'Error generating Jupyter notebook: {e}')

        self.link_jupyter_notebook(file_name)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        '''
        Normalizes the ELN entry to generate a Jupyter notebook.
        '''

        self.write_jupyter_notebook(archive, logger)

        super().normalize(archive, logger)

m_package.__init_metainfo__()
