'''
    Contains analysis functions which will be included in the Jupyter analysis notebook.

    The functions should be added along its category using the `category` decorator. The
    category should be correspond to `analysis_type` in the schema.

    At present, the experiment specific categories includes `XRD`.
    For e.g., when adding an analysis function for XRD, use `@category('XRD')` decorator.

    Use `@category('Generic')` for functions which should always be included.

    Important:
        Necessary library or module imports should be included inside the function.
        This will allow the imports to be specified in the generated Jupyter notebook.
'''
from analysis.utils import category

@category('Generic')
def get_input_data(token_header: dict, base_url: str, analysis_entry_id: str) -> list:
    '''
    Gets the archive data of all the referenced input entries.

    Args:
        token_header (dict): Authentication token.
        base_url (str): Base URL of the NOMAD API.
        analysis_entry_id (str): Entry ID of the analysis ELN.

    Returns:
        list: List of data from all the referenced entries.
    '''
    import requests

    def entry_id_from_reference(reference: str):
        return reference.split('#')[0].split('/')[-1]

    query = {
        "required" : {
            "data": "*",
        }
    }
    response = requests.post(
        f"{base_url}/entries/{analysis_entry_id}/archive/query",
        headers = {
            **token_header,
            'Accept': 'application/json'
        },
        json = query
    ).json()
    referred_entries = response['data']['archive']['data']['inputs']

    entry_ids = []
    for entry in referred_entries:
        entry_ids.append(entry_id_from_reference(entry['reference']))

    entry_archive_data_list = []
    for entry_id in entry_ids:
        response = requests.post(
            f"{base_url}/entries/{entry_id}/archive/query",
            headers = {
                **token_header,
                'Accept': 'application/json'
            },
            json = query
        ).json()
        if 'data' in response.keys():
            entry_archive_data_list.append(response['data']['archive']['data'])

    return entry_archive_data_list

@category('XRD')
def xrd_plot_intensity_two_theta(archive_data: dict, peak_indices = None) -> None:
    '''
    Generates a 2D plot of intensity vs 2θ with linear x and y axis.

    Args:
        archive_data (dict): Archive data of the entry.
        peak_indices (np.array): Indices of peaks found in the intensity data.
    '''
    import plotly.express as px
    import numpy as np

    intensity = np.array(archive_data['results'][0]['intensity'])
    two_theta = np.array(archive_data['results'][0]['two_theta'])

    line_linear = px.line(
            x=two_theta,
            y=intensity,
            labels={
                'x': '2θ (°)',
                'y': 'Intensity',
            },
            height=600,
            width=800,
            title='Intensity vs 2θ (linear scale)',
        )
    if peak_indices is not None or len(peak_indices) > 0:
        line_linear.add_scatter(
            x=two_theta[peak_indices],
            y=intensity[peak_indices],
            mode='markers',
            marker=dict(
                size=8,
                color='red',
                symbol='cross'
            ),
            name='Peaks',
        )
    line_linear.show()

@category('XRD')
def xrd_plot_logy_intensity_two_theta(archive_data: dict, peak_indices = None) -> None:
    '''
    Generates a 2D plot of intensity vs 2θ with linear x and log y axis.

    Args:
        archive_data (dict): Archive data of the entry.
        peak_indices (np.array): Indices of peaks found in the intensity data.
    '''
    import plotly.express as px
    import numpy as np

    intensity = np.array(archive_data['results'][0]['intensity'])
    two_theta = np.array(archive_data['results'][0]['two_theta'])

    line_log = px.line(
        x=two_theta,
        y=intensity,
        log_y=True,
        labels={
            'x': '2θ (°)',
            'y': 'Intensity',
        },
        height=600,
        width=800,
        title='Intensity vs 2θ (log scale)',
    )
    if peak_indices is not None or len(peak_indices) > 0:
        line_log.add_scatter(
            x=two_theta[peak_indices],
            y=intensity[peak_indices],
            mode='markers',
            marker=dict(
                size=8,
                color='red',
                symbol='cross'
            ),
            name='Peaks',
        )
    line_log.show()

@category('XRD')
def xrd_find_peaks(archive_data: dict, options: dict = None) -> dict:
    '''
    Finds the peaks in the intensity vs 2θ plot.

    Args:
        archive_data (dict): Archive data of the entry.
        options (dict): Options for the peak finding algorithm `scipy.signal.find_peaks`.

    Returns:
        dict: Peaks found in the intensity vs 2θ plot.
    '''
    import numpy as np
    from scipy.signal import find_peaks

    intensity = np.array(archive_data['results'][0]['intensity'])
    two_theta = np.array(archive_data['results'][0]['two_theta'])

    if options:
        peak_indices, _ = find_peaks(intensity, **options)
    else:
        peak_indices, _ = find_peaks(intensity)

    peaks_intensity = intensity[peak_indices]
    peaks_two_theta = two_theta[peak_indices]

    peaks = {
        'peaks': {
            'intensity': peaks_intensity.tolist(),
            'two_theta': peaks_two_theta.tolist(),
        }
    }

    return peaks, peak_indices

@category('XRD')
def xrd_save_analysis_results(
    results: dict, file_name: str = 'tmp_analysis_results.json'
):
    '''
    Saves the analysis results as a json file.

    Args:
        results (dict): Analysis results.
        file_name (str): Name of the file to save the results.
    '''
    import json

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(results, f)

@category('XRD')
def xrd_conduct_analysis(
    archive_data: dict,
    options: dict = None,
    plot: bool = True,
) -> None:
    '''
    Conducts XRD analysis on the given archive data. Also saves the analysis results as
    a json file which can be used to fill `analysis_results` section.

    Args:
        archive_data (dict): Archive data of the entry.
        plot (bool): If True, plots the intensity vs 2θ plot.
    '''
    import collections

    if options is None:
        options = {
            'height': 20,
            'threshold': 30,
            'distance': 1,
        }
    peaks, peak_indices = xrd_find_peaks(archive_data, options = options)
    if plot:
        xrd_plot_intensity_two_theta(archive_data, peak_indices)
        xrd_plot_logy_intensity_two_theta(archive_data, peak_indices)

    results = collections.defaultdict(None)
    results['peaks'] = peaks

    xrd_save_analysis_results(results)

@category('XRD')
def xrd_voila_analysis(input_data) -> None:
    '''
    Use ipywidgets to create an interactive XRD analysis. These widgets can be rendered
    using Voila.
    '''
    ## Voila specific code

    import ipywidgets as widgets
    from IPython.display import display, clear_output

    def get_input_entry_names(input_data: list) -> list:
        '''
        Gets the names of the input entries.

        Args:
            input_data (list): List of input data.

        Returns:
            list: Names of the input entries.
        '''
        names = []
        for entry in input_data:
            if entry['m_def'] == 'nomad_measurements.xrd.schema.ELNXRayDiffraction':
                names.append(entry['name'])
        return names

    available_entries = get_input_entry_names(input_data)
    dropdown = widgets.Dropdown(options=available_entries)
    find_peak_parameters = [
        widgets.FloatText(
            description = 'Height:',
            value = 10,
            readout_format = '.1f',
            tooltip = 'Required height of peaks.',
        ),
        widgets.FloatText(
            description = 'Threshold:',
            value = 10,
            readout_format = '.1f',
            tooltip = 'Required threshold of peaks, the vertical distance'
                'to its neighboring samples.',
        ),
        widgets.FloatText(
            description = 'Distance:',
            value = 1,
            readout_format = '.1f',
            tooltip = 'Required minimal horizontal distance (>= 1) in samples'
                'between neighbouring peaks.',
        ),
    ]
    find_peak_button = widgets.Button(
                    description = 'Find peaks',
                    button_style = 'primary',
                )

    no_input_alert = widgets.HTML('<p style="color:red;">No input entry of class'
                                '`ELNXRayDiffraction` found.</p>')
    no_input_alert.layout.visibility = 'hidden'

    input_box = widgets.VBox([
        widgets.HTML('<h1>XRD Analysis</h1>'),
        widgets.Label(value='Select input entry:'),
        dropdown,
        widgets.VBox([
            widgets.HTML('<h2>Locate the intensity peaks</h2>\
                        Select the parameters for peak finding algorithm:'),
            widgets.HBox(
                find_peak_parameters
            ),
            widgets.HTML('<br>'),
            find_peak_button,
        ]),
        no_input_alert,
        ]
    )

    if not available_entries:
        no_input_alert.layout.visibility = 'visible'
        dropdown.disabled = True
        find_peak_button.disabled = True

    out = widgets.Output(
        layout = dict(),
    )

    def on_click_find_peaks(button):
        '''
        Event handler for the button click.
        '''
        if find_peak_parameters[2].value < 1:
            find_peak_parameters[2].value = 1
        entry_name = dropdown.value
        entry_index = get_input_entry_names(input_data).index(entry_name)

        with out:
            options = {
                'height': find_peak_parameters[0].value,
                'threshold': find_peak_parameters[1].value,
                'distance': find_peak_parameters[2].value,
            }
            xrd_conduct_analysis(
                archive_data = input_data[entry_index],
                options = options,
                plot = True)
            clear_output(wait=True)

    find_peak_button.on_click(on_click_find_peaks)

    display(input_box, out)
