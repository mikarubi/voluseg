import json
import numpy as np


def _check_json_filename(filename: str) -> None:
    if not filename.lower().endswith(".json"):
        raise ValueError(f"Parameters file must be a .json file, got: {filename}")


def load_parameters(filename: str) -> dict:
    """
    Load previously saved parameters from a JSON file.

    Parameters
    ----------
    filename : str
        Filename of parameter file.

    Returns
    -------
    dict
        Parameters dictionary.
    """
    _check_json_filename(filename)
    with open(filename, "r") as file_handle:
        parameters = json.load(file_handle)

    # convert lists to numpy arrays
    for key, value in parameters.items():
        if isinstance(value, list):
            parameters[key] = np.array(value)

    return parameters


def numpy_converter(obj):
    """Convert NumPy arrays to lists for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_parameters(parameters: dict, filename: str) -> None:
    """
    Save parameters to a JSON file.

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
    _check_json_filename(filename)
    with open(filename, "w") as file_handle:
        json.dump(parameters, file_handle, indent=4, default=numpy_converter)

    print(f"Parameters successfully saved to: {filename}.")
