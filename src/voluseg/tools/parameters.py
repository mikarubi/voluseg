import pickle
import json
from voluseg.tools.parameters_models import ParametersModel


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
    # Validate parameters
    try:
        parameters_model = ParametersModel(**parameters)
    except Exception as e:
        raise Exception(f"Parameters file is not valid: {e}.")
    print("Parameters file successfully loaded and validated.")
    return parameters_model.model_dump(use_np_array=True)


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
    # Validate parameters
    try:
        parameters_model = ParametersModel(**parameters)
        parameters = parameters_model.model_dump(use_np_array=False)
    except Exception as e:
        raise Exception(f"Parameters are not valid: {e}.")
    if filename.split(".")[-1] in ["pickle", "pkl"]:
        with open(filename, "wb") as file_handle:
            pickle.dump(parameters, file_handle)
    elif filename.split(".")[-1] == "json":
        with open(filename, "w") as file_handle:
            json.dump(parameters, file_handle, indent=4)
    else:
        raise Exception("Parameters file must be either a pickle or a json file.")
    print(f"Parameters successfully saved to: {filename}.")
