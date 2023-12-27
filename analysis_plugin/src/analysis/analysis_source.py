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
def get_entry_archive_data(token_header: dict, base_url: str, entry_id: str) -> dict:
    '''
    Gets the archive data of an entry.

    Args:
        token_header (dict): Authentication token.
        base_url (str): Base URL of the NOMAD API.
        entry_id (str): Entry ID of the entry.

    Returns:
        dict: Data of the entry.
    '''
    import requests

    query = {
        "required" : {
            "data": "*",
        }
    }
    response = requests.post(
        f"{base_url}/entries/{entry_id}/archive/query",
        headers = token_header,
        json = query
    ).json()
    if 'data' in response.keys():
        return response['data']['archive']['data']
    return response

@category('XRD')
def xrd_plot_intensity_two_theta(archive_data: dict) -> None:
    '''
    Generates a 2D plot of intensity vs 2θ with linear x and y axis.

    Args:
        archive_data (dict): Archive data of the entry.
    '''
    import plotly.express as px

    intensity = archive_data['results'][0]['intensity']
    two_theta = archive_data['results'][0]['two_theta']

    line_linear = px.line(
            x=two_theta,
            y=intensity,
            labels={
                'x': '2θ (°)',
                'y': 'Intensity',
            },
            title='Intensity vs 2θ (linear scale)',
        )
    line_linear.show()

@category('XRD')
def xrd_plot_logy_intensity_two_theta(archive_data: dict) -> None:
    '''
    Generates a 2D plot of intensity vs 2θ with linear x and log y axis.

    Args:
        archive_data (dict): Archive data of the entry.
    '''
    import plotly.express as px

    intensity = archive_data['results'][0]['intensity']
    two_theta = archive_data['results'][0]['two_theta']

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
    line_log.show()
