def load_parameters(filename):
    """load previously saved parameters from filename"""

    import pickle

    try:
        with open(filename, "rb") as file_handle:
            parameters = pickle.load(file_handle)

        print("parameter file successfully loaded.")
        return parameters

    except Exception as msg:
        print("parameter file not loaded: %s." % (msg))
