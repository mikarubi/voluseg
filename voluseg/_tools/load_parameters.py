import pickle


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
    try:
        with open(filename, "rb") as file_handle:
            parameters = pickle.load(file_handle)

        print("parameter file successfully loaded.")
        return parameters

    except Exception as msg:
        print("parameter file not loaded: %s." % (msg))
