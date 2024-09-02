import pickle
import json


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
    if filename.split(".")[-1] == "pickle":
        with open(filename, "rb") as file_handle:
            parameters = pickle.load(file_handle)
    elif filename.split(".")[-1] == "json":
        with open(filename, "r") as file_handle:
            parameters = json.load(file_handle)
    else:
        raise Exception("parameter file must be either a pickle or a json file.")
    print("parameter file successfully loaded.")
    return parameters
