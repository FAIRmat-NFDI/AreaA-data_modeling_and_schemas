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
def xrd_conduct_analysis(archive_data: dict, plot: bool = True) -> None:
    '''
    Conducts XRD analysis on the given archive data. Also saves the analysis results as
    a json file which can be used to fill `analysis_results` section.

    Args:
        archive_data (dict): Archive data of the entry.
        plot (bool): If True, plots the intensity vs 2θ plot.
    '''
    import collections

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
