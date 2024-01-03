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
Schema for analysis using Jupyter notebooks.
Allows the user to connect input sections through references. The entry archives from the
input sections are linked and imported into the generated Jupyter notebook.
The notebook can be used to interactively analyse the data from these entry archives.

Schema also allows the user to define the analysis type. Based on the analysis type,
pre-defined code cells are added to the notebook. For example, if the analysis type is
XRD, then the notebook will have pre-defined code cells for XRD analysis. By default,
the analysis type is set to Generic, which includes functions and statements to connect
with the entry archives.

Upcoming features:
- Link the output section of the analysis schema to a sub-section of the input.
- Write the analysis results back to the output section.
'''
from typing import (
    TYPE_CHECKING
)
import nbformat as nbf
import json
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
        default = 'Generic',
        description = (
            'Based on the analysis type, code cells will be added to the Jupyter '
            'notebook. Code cells from **Generic** are always included.'
            '''
            | Analysis Type       | Description                                     |
            |---------------------|-------------------------------------------------|
            | **Generic**         | (Default) Basic setup including connection \
                                    with entry data.                                |
            | **XRD**             | Adds XRD related analysis functions.            |
            '''
        )
        ,
        a_eln = ELNAnnotation(
            label = 'Analysis Type',
            component = ELNComponentEnum.EnumEditQuantity,
        ),
    )
    reset_notebook = Quantity(
        type = bool,
        description = (
            '**Caution** This will reset the pre-defined cells of the notebook. '
            'All customization to these cells will be lost.\n'
            'In case the notebook is not available as a raw file, it will be generated.\n'
            'Resetting or generating a notebook will be based on the analysis type.'
        ),
        default = True,
        a_eln = ELNAnnotation(
            label = 'Reset pre-defined cells in Notebook',
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
        '''
        Links the Jupyter notebook from raw folder to the ELN entry.

        Args:
            path (str): Path of the Jupyter notebook.
        '''
        self.notebook = path

    def write_predefined_cells(
            self, archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> list:
        '''
        Writes the pre-defined Jupyter notebook cells based on the analysis type.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        entry_ids = []
        if self.inputs is not None:
            for entry in self.inputs:
                entry_ids.append(entry.reference.m_parent.entry_id)
        if len(entry_ids) == 0:
            logger.warning('No EntryArchive linked.')

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
        f'base_url = "{archive.m_context.installation_url}"\n'
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
            cells.append(nbf.v4.new_code_cell(source = comment + code))

        return cells

    def generate_jupyter_notebook(
        self, archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> None:
        '''
        Generates the notebook `ELNJupyterAnalysis.ipynb` and saves it in `raw` folder.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        nb = nbf.v4.new_notebook()

        cells = self.write_predefined_cells(archive, logger)

        cells.append(nbf.v4.new_code_cell())
        cells.append(nbf.v4.new_code_cell())
        cells.append(nbf.v4.new_code_cell())

        for cell in cells:
            nb.cells.append(cell)

        file_name = 'ELNJupyterAnalysis.ipynb'
        with archive.m_context.raw_file(file_name, 'w') as nb_file:
            nbf.write(nb, nb_file)
        archive.m_context.process_updated_raw_file(file_name, allow_modify=True)

        self.link_jupyter_notebook(file_name)

    def overwrite_jupyter_notebook(
        self, archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> None:
        '''
        Overwrites the Jupyter notebook to reset predefined cells while preserving the
        other user-defined cells.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        cells = self.write_predefined_cells(archive, logger)

        with archive.m_context.raw_file(self.notebook, 'r') as nb_file:
            nb = nbf.read(nb_file, as_version=nbf.NO_CONVERT)

        for cell in nb.cells:
            if cell.source.startswith('# Pre-defined block'):
                continue
            cells.append(cell)

        nb.cells = cells

        with archive.m_context.raw_file(self.notebook, 'w') as nb_file:
            nbf.write(nb, nb_file)
        archive.m_context.process_updated_raw_file(self.notebook, allow_modify=True)

    def write_jupyter_notebook(
        self, archive: 'EntryArchive', logger: 'BoundLogger'
    ) -> None:
        '''
        Writes the Jupyter notebook based on the analysis type.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        if not self.notebook or not archive.m_context.raw_path_exists(self.notebook):
            self.generate_jupyter_notebook(archive, logger)
        else:
            self.overwrite_jupyter_notebook(archive, logger)

    def write_results(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        '''
        Writes the results of the analysis to the output section.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        '''
        if archive.m_context.raw_path_exists('tmp_analysis_results.json'):
            with archive.m_context.raw_file('tmp_analysis_results.json', 'r') as f:
                data = json.load(f)
            # TODO add results to output, delete tmp_analysis_results.json

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
