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
    MEnum,
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
from analysis.utils import (
    get_function_source,
    list_to_string
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

m_package = Package(name = 'analysis_jupyter')

class JupyterAnalysisResult(AnalysisResult):
    '''
    Section for collecting Jupyter notebook analysis results.
    It is a non-editable section that is populated once the processing is.

    TODO: One can also create a custom schema for results and
    define it as a sub-section here.
    '''
    m_def = Section(
        label = 'Jupyter Notebook Analysis Results',
    )
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
    )
    outputs = SubSection(
        section_def = SectionReference,
        description = 'The result section for the analysis',
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
    analysis_type = Quantity(
        type = MEnum(
            [
                'Generic',
                'XRD',
            ]
        ),
        description = 'Type of analysis',
        a_eln = ELNAnnotation(
            label = 'Analysis Type',
            component = ELNComponentEnum.EnumEditQuantity,
            default = 'Generic',
        ),
    )
    reset_notebook = Quantity(
        type = bool,
        description = (
            'Caution: This will reset the entire notebook and all customizations '
            'will be lost.'
        ),
        default = True,
        a_eln = ELNAnnotation(
            label = 'Reset Notebook',
            component = ELNComponentEnum.BoolEditQuantity,
        ),
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
            '# Pre-defined block\n'
            '\n'
            '# This notebook has been generated by "Jupyter Notebook Analysis" with the '
            f'name "{self.name}"\n'
            '# It gets the data from the entries available in the current upload.\n'
            '# It also gets the analysis function based on the analysis type (e.g., XRD).'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            generic_analysis_functions = get_function_source(category_name='Generic')
            generic_analysis_functions = list_to_string(generic_analysis_functions)

            code = (
            '# Pre-defined block\n'
            '\n'
            'import requests\n'
            'from nomad.client import Auth\n'
            '\n'
            'base_url = "http://nomad-lab.eu/prod/v1/api/v1"\n'
            'token_header = Auth().headers()\n'
            '\n'
            f'{generic_analysis_functions}'
            'entry_archive_data_list = []\n'
            f'for entry_id in {entry_ids}:\n'
            '   entry_archive_data_list.append('
            'get_entry_archive_data(token_header, base_url, entry_id))\n'
            '\n'
            'print(f"Retrieved {len(entry_archive_data_list)} entry(ies). Please check '
            'the contents by accessing `entry_archive_data_list`.")\n'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            code = (
                '# Pre-defined block\n'
                '\n'
                'entry_archive_data_list[0].keys()'
            )
            cells.append(nbf.v4.new_code_cell(source=code))

            if self.analysis_type is not None and self.analysis_type != 'Generic':
                comment = (
                    '# Pre-defined block\n'
                    '\n'
                    f'# Analysis functions specific to "{self.analysis_type}".\n'
                    '\n'
                )
                analysis_functions = get_function_source(category_name=self.analysis_type)
                code = list_to_string(analysis_functions)
                cells.append(nbf.v4.new_code_cell(source=comment+code))

            cells.append(nbf.v4.new_code_cell())
            cells.append(nbf.v4.new_code_cell())
            cells.append(nbf.v4.new_code_cell())

            nb = nbf.v4.new_notebook()
            for cell in cells:
                nb.cells.append(cell)

            with archive.m_context.raw_file(file_name, 'w') as nb_file:
                nbf.write(nb, nb_file)
            archive.m_context.process_updated_raw_file(file_name, allow_modify=True)

        except Exception as e:
            logger.error(f'Error generating Jupyter notebook: {e}')

        self.link_jupyter_notebook(file_name)

    def write_results(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        Writes the results of the analysis to the JupyterAnalysisResult section.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        results = JupyterAnalysisResult(
            connection_status = 'Connected',
        )
        results.normalize(archive, logger)
        self.outputs.append(results)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        '''
        Normalizes the ELN entry to generate a Jupyter notebook.
        '''
        if self.reset_notebook:
            self.write_jupyter_notebook(archive, logger)
            self.reset_notebook = False
        self.write_results(archive, logger)

        super().normalize(archive, logger)

m_package.__init_metainfo__()
