import json
import pickle
import numpy as np


def load_parameters(filename: str) -> dict:
    """
    Load previously saved parameters from filename.

    Parameters
    ----------
    filename : str
        Filename of parameter file.

    Returns
    -------
    dict
        Parameters dictionary.
    """
    if filename.split(".")[-1] in ["pickle", "pkl"]:
        with open(filename, "rb") as file_handle:
            parameters = pickle.load(file_handle)
    elif filename.split(".")[-1] == "json":
        with open(filename, "r") as file_handle:
            parameters = json.load(file_handle)
    else:
        raise Exception("Parameters file must be either a pickle or a json file.")

    # convert lists to numpy arrays
    for key, value in parameters.items():
        if isinstance(value, list):
            parameters[key] = np.array(value)

    return parameters


def save_parameters(parameters: dict, filename: str) -> None:
    """
    Save parameters to filename.

    Parameters
    ----------
    parameters : dict
        Parameters dictionary.
    filename : str
        Filename of parameter file.

    Returns
    -------
    None
    """
    if filename.split(".")[-1] in ["pickle", "pkl"]:
        with open(filename, "wb") as file_handle:
            pickle.dump(parameters, file_handle)
    elif filename.split(".")[-1] == "json":
        with open(filename, "w") as file_handle:
            json.dump(parameters, file_handle, indent=4)
    else:
        raise Exception("Parameters file must be either a pickle or a json file.")
    print(f"Parameters successfully saved to: {filename}.")
