# Imports
import os
import getopt
import sys
from urllib.error import HTTPError
import pandas as pd
import requests
from typing import Callable, Mapping, Union, Optional
from math import isnan

# Aliases
StringToInt = Union[Mapping[str, int], Callable[[str], int]]

# Constants
OSF_PROJECT = 'https://doi.org/10.17605/osf.io/74bzs'
OUTPUT_PATH = './data'
COMPILED_DATA_PATH = f'{OUTPUT_PATH}/compiled-survey-data.csv'
RAW_DATA_NAME = 'qualtrics-survey-data.csv'

def remap_to_int(value: Union[str, float], mapper: StringToInt, nan: int = -1) -> int:
    """Remaps a string value to an integer based on the provided mapper.

    Parameters
    ----------
    value : str or float
        The value to be transformed.
    mapper : Mapping-like object or Callable-like object
        The mapper used to transform the string to a value.
    nan : int (default -1)
        The value to return when a NaN value is provided.
    
    Returns
    -------
    int
        The value represented as an integer.
    
    Raises
    ------
    KeyError
        If the mapper is a Mapping-like object and the key does not exist.
    
    """

    if type(value) == float and isnan(value):
        return nan
    elif callable(mapper):
        return mapper(value)
    else:
        return mapper[value]

def remap_yes_no(value: Union[str, float]) -> int:
    """Remaps a 'Yes'/'No' to 1/0 respectively.
    
    Parameters
    ----------
    value : str or float
        The value to be transformed.
    
    Returns
    -------
    int
        The value represented as an integer.
    
    Raises
    ------
    KeyError
        If the mapper is a Mapping-like object and the key does not exist.
    """
    return remap_to_int(
        value = value,
        mapper = {
            'Yes': 1,
            'No': 0
        }
    )

def remap_list(values: str, index_mapper: StringToInt) -> int:
    """Remaps a string list to a bit field stored in an integer.

    The mapper returns an index representing the position in the bit field
    the string represents.

    The value is expected to be comma separated and not enclosed in
    quotations.

    Parameters
    ----------
    values : str
        The non-enclosed string list
    index_mapper : Mapping-like object or Callable-like object
        The mapper used to transform the string to a index.
    
    Returns
    -------
    int
        The string list represented as a bit field within an integer.
    
    Raises
    ------
    KeyError
        If the mapper is a Mapping-like object and the key does not exist.
    """
    mapper: Callable[[str], int] = lambda value: index_mapper(value) if callable(index_mapper) else index_mapper[value]
    result: int = 0
    for value in values.split(','):
        result = result | (1 << mapper(value))
    return result

def download_data(path: str, remote: str, name: Optional[str] = None, loc: Optional[str] = None):
    """Downloads a file from a remote location to the specified path
    using a GET request. 
    
    Parameters
    ----------
    path : str
        The path on the machine where the file should be downloaded to.
    remote : str
        The remote location which can be queried with a GET request.
    name : str (default path)
        The name of the file that is being pulled from the remote.
    loc : str (default remote)
        The location where the remote file lives.
    
    Raises
    ------
    HTTPError
        If the file could not be downloaded from the remote location.
    """
    if loc is None:
        loc = remote
    if name is None:
        name = path

    if not os.path.exists(path):
        print(f'Downloading {name} from \'{loc}\'.')

        # Download data
        response: requests.Response = requests.get(remote)
        if not response.ok:
            raise HTTPError(f'Failed to download {name} from \'{loc}\'.')

        # Write data to location
        with open(path, 'wb') as data:
            data.write(response.content)

# Main code

if __name__ == '__main__':

    # Get command line args if present
    raw_dataset: bool = os.getenv('74BZS_RAW_DATASET') is not None and os.getenv('74BZS_RAW_DATASET').lower() in ['true', '1', 't', 'y', 'yes']
    docs: bool = os.getenv('74BZS_DOCS') is None or os.getenv('74BZS_DOCS').lower() in ['true', '1', 't', 'y', 'yes']
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hrn', ['help', 'raw-dataset', 'no-docs'])
    except getopt.GetoptError:
        print('qualtrics_data_compiler.py [-h | --help] [-r | --raw-dataset] [-n | --no-docs]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('qualtrics_data_compiler.py [-h | --help] [-r | --raw-dataset] [-n | --no-docs]')
            sys.exit(0)
        elif opt in ('-r', '--raw-dataset'):
            raw_dataset = True
        elif opt in ('-n', '--no-docs'):
            docs = False


    # Create output folder if it does not exist
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)

    # Short circuit if compiled data already exists
    if os.path.exists(COMPILED_DATA_PATH):
        print(f'Compiled file \'{COMPILED_DATA_PATH}\' already exists, exiting early.')
        sys.exit(0)

    # Set the path to get the raw data
    raw_data_path: str = f'{OUTPUT_PATH}/{RAW_DATA_NAME}' if raw_dataset else RAW_DATA_NAME

    # Download raw data if it doesn't exist
    download_data(raw_data_path, 'https://osf.io/download/q2bxh/', RAW_DATA_NAME, OSF_PROJECT)

    # Load in data to frame
    ## Remove metadata rows provided by Qualtrics
    ## Set index column to the DOI
    data: pd.DataFrame = pd.read_csv(raw_data_path, skiprows=[0,2], index_col='Paper DOI Link')

    # Rename and reorder columns
    data = data.rename(columns = {
        'Open Data': 'open_data',
        'Open Materials': 'open_materials',
        'Conference Proceedings': 'conference_proceedings',
        'Type': 'paper_type',
        'Misclassified': 'acm_misclassified',
        'Open Methodology': 'open_methodology',
        'Data Documentation': 'data_documentation',
        'Materials Documentation': 'materials_documentation',
        'README': 'readme',
        'License': 'permissible_software_license',
        'Preregistration': 'preregistration',
        'Reproducible': 'reproducible',
        'Reference Degradation': 'reference_degradation'
    })
    data.index.name = 'doi'
    data = data[[
            'conference_proceedings',
            'paper_type',
            'acm_misclassified',
            'open_methodology',
            'open_data',
            'data_documentation',
            'open_materials',
            'materials_documentation',
            'readme',
            'permissible_software_license',
            'preregistration',
            'reproducible',
            'reference_degradation'
        ]
    ]

    # Remap columns
    data['paper_type'] = data['paper_type'].map(lambda value: remap_to_int(
        value = value,
        mapper = {
            'Research Article': 1,
            'Short paper': 2,
            'Poster': 3
        }
    ))
    data['acm_misclassified'] = data['acm_misclassified'].map(remap_yes_no)
    data['open_methodology'] = data['open_methodology'].map(lambda value: remap_to_int(
        value = value,
        mapper = {
            'Public Access': 3,
            'Open Access': 2,
            'Available': 1,
            'No': 0
        }
    ))
    data['open_data'] = data['open_data'].map(lambda value: remap_to_int(
        value = value,
        mapper = {
            'Yes': 2,
            'Data Available on Request': 1,
            'No': 0
        }
    ))
    data['data_documentation'] = data['data_documentation'].map(lambda value: remap_to_int(
        value = value,
        mapper = {
            'Yes': 2,
            'Partial': 1,
            'No': 0
        }
    ))
    data['open_materials'] = data['open_materials'].map(lambda value: remap_to_int(
        value = value,
        mapper = {
            'Full': 3,
            'Partial': 2,
            'On Request': 1,
            'No': 0
        }
    ))
    data['materials_documentation'] = data['materials_documentation'].map(lambda value: remap_to_int(
        value = value,
        mapper = {
            'Full': 2,
            'Partial': 1,
            'No': 0
        }
    ))
    data['readme'] = data['readme'].map(remap_yes_no)
    data['permissible_software_license'] = data['permissible_software_license'].map(remap_yes_no)
    data['preregistration'] = data['preregistration'].map(remap_yes_no)
    data['reproducible'] = data['reproducible'].map(remap_yes_no)
    data['reference_degradation'] = data['reference_degradation'].map(lambda values: remap_to_int(
        value = values,
        mapper = lambda v: remap_list(
            values = v,
            index_mapper = {
                'Open Methodology': 0,
                'Open Data': 1,
                'Open Materials': 2,
                'Preregistration': 3
            }
        ),
        nan = 0
    ))

    # Pull supplemental documents
    if docs:
        download_data(f'{OUTPUT_PATH}/CONTENT-LICENSE', 'https://osf.io/download/4xhm9/', 'CONTENT-LICENSE', OSF_PROJECT)
        download_data(f'{OUTPUT_PATH}/dataset-description.pdf', 'https://osf.io/download/bgwp3/', 'dataset-description.pdf', OSF_PROJECT)
        download_data(f'{OUTPUT_PATH}/explanations.pdf', 'https://osf.io/download/xav7z/', 'explanations.pdf', OSF_PROJECT)


    # Export compiled data to csv
    data.to_csv(COMPILED_DATA_PATH)

    # Finish execution
    sys.exit(1)