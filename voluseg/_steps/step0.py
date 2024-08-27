import os
import copy
import pickle
import numpy as np
from warnings import warn
from voluseg._tools.load_volume import load_volume
from voluseg._tools.get_volume_name import get_volume_name
from voluseg._tools.parameter_dictionary import parameter_dictionary
from voluseg._tools.evenly_parallelize import evenly_parallelize
from voluseg._tools.nwb import open_nwbfile_local


def process_parameters(parameters0: dict) -> None:
    """
    Process parameters and create parameter file.

    Parameters
    ----------
    parameters0 : dict
        Initial parameter dictionary

    Returns
    -------
    None
    """
    parameters = copy.deepcopy(parameters0)

    ## general checks

    # check that parameter input is a dictionary
    if not isinstance(parameters, dict):
        raise Exception("specify parameter dictionary as input.")

    # check if any parameters are missing
    missing_parameters = set(parameter_dictionary()) - set(parameters)
    if missing_parameters:
        raise Exception("missing parameters '%s'." % ("', '".join(missing_parameters)))

    # get input and output directories, and parameter filename
    dir_input = parameters["dir_input"]
    dir_output = parameters["dir_output"]
    filename_parameters = os.path.join(dir_output, "parameters.pickle")

    # load parameters from file, if it already exists
    if os.path.isfile(filename_parameters):
        print("exiting, parameter file exists: %s." % (filename_parameters))
        return

    ## specific checks

    # check strings
    for i in [
        "dir_ants",
        "dir_input",
        "dir_output",
        "dir_transform",
        "registration",
        "registration_restrict",
    ]:
        pi = parameters[i]
        if not (isinstance(pi, str) and (" " not in pi)):
            raise Exception("'%s' must be a string without spaces." % (i))

    # check booleans
    for i in ["parallel_clean", "parallel_volume", "planes_packed", "save_volume"]:
        pi = parameters[i]
        if not isinstance(pi, bool):
            raise Exception("'%s' must be a boolean." % (i))

    # check integers
    for i in ["ds", "n_cells_block", "n_colors", "planes_pad"]:
        pi = parameters[i]
        if not (np.isscalar(pi) and (pi >= 0) and (pi == np.round(pi))):
            raise Exception("'%s' must be a nonnegative or positive integer." % (i))

    # check non-negative real numbers:
    for i in [
        "diam_cell",
        "f_hipass",
        "f_volume",
        "res_x",
        "res_y",
        "res_z",
        "t_baseline",
        "t_section",
        "thr_mask",
    ]:
        pi = parameters[i]
        if not (np.isscalar(pi) and (pi >= 0) and np.isreal(pi)):
            raise Exception("'%s' must be a nonnegative or positive real number." % (i))

    # check detrending
    if parameters["detrending"]:
        parameters["detrending"] = parameters["detrending"].lower()
        if parameters["detrending"] == "none":
            parameters["detrending"] = None
        elif not parameters["detrending"] in ["standard", "robust"]:
            raise Exception("'detrending' must be 'standard', 'robust', or 'none'.")

    # check registration
    if parameters["registration"]:
        parameters["registration"] = parameters["registration"].lower()
        if parameters["registration"] == "none":
            parameters["registration"] = None
        elif not parameters["registration"] in ["high", "medium", "low", "transform"]:
            raise Exception(
                "'registration' must be 'high', 'medium', 'low', 'none' or 'transform'."
            )

    # check registration restrict
    if parameters["registration_restrict"]:
        parameters["registration_restrict"] = parameters[
            "registration_restrict"
        ].lower()
        if not set(["0", "1"]) == set(parameters["registration_restrict"].split("x")):
            raise Exception(
                "'registration_restrict' must comprise '1's and '0's, separated by 'x's."
            )

    # check type of mask
    parameters["type_mask"] = parameters["type_mask"].lower()
    if not parameters["type_mask"] in ["mean", "geomean", "max"]:
        raise Exception("'type_mask' must be 'mean', 'geomean', or 'max'.")

    # check plane padding
    if (not parameters["registration"]) and not ((parameters["planes_pad"] == 0)):
        raise Exception("'planes_pad' must be 0 if 'registration' is None.")

    # convert dir_input into a list to account for multiple directories
    input_dirs = [os.path.normpath(h) for h in dir_input.split(";")]
    if len(input_dirs) == 1:
        prefix_dirs = [None]
    else:
        prefix_dirs = [os.path.basename(h) for h in input_dirs]
        if len(prefix_dirs) != len(set(prefix_dirs)):
            raise Exception(
                "the names of last directories in 'dir_input' must be unique."
            )
        if prefix_dirs != sorted(prefix_dirs):
            raise Exception(
                "the names of last directories in 'dir_input' must be sorted."
            )

    volume_fullnames_input = []
    volume_names = []
    if parameters.get("nwb_input_local_path", None):
        acquisition_name = parameters.get("nwb_input_acquisition_name", None)
        if not acquisition_name:
            raise Exception("nwb_input_acquisition_name is required to read nwb file")
        volume_fullnames_input = [parameters.get("nwb_input_local_path")]
        volume_names = [
            parameters.get("nwb_input_local_path").split("/")[-1].split(".nwb")[0]
        ]
        with open_nwbfile_local(
            file_path=parameters["nwb_input_local_path"]
        ) as nwbfile:
            lt = nwbfile.acquisition[acquisition_name].data.shape[0]
            if parameters["timepoints"]:
                lt = min(lt, parameters["timepoints"])
        ext = ".nwb"
    else:
        for dir_input_h, dir_prefix_h in zip(input_dirs, prefix_dirs):
            # get volume extension, volume names and number of segmentation timepoints
            file_names = [i.split(".", 1) for i in os.listdir(dir_input_h) if "." in i]
            file_exts, counts = np.unique(list(zip(*file_names))[1], return_counts=True)
            ext = "." + file_exts[np.argmax(counts)]
            volume_names_input_h = sorted([i for i, j in file_names if "." + j == ext])
            volume_fullnames_input_h = [
                os.path.join(dir_input_h, i) for i in volume_names_input_h
            ]

            # adjust parameters for packed planes data
            if parameters["planes_packed"]:
                parameters["res_z"] = parameters["diam_cell"]

                def get_plane_names(tuple_fullname_volume_input):
                    fullname_volume_input = tuple_fullname_volume_input[1]
                    lp = len(load_volume(fullname_volume_input + ext))
                    return [
                        get_volume_name(fullname_volume_input, dir_prefix_h, pi)
                        for pi in range(lp)
                    ]

                volume_names_h = (
                    evenly_parallelize(volume_fullnames_input_h)
                    .map(get_plane_names)
                    .collect()
                )
                volume_names_h = [pi for ni in volume_names_h for pi in ni]
            else:
                volume_names_h = [
                    get_volume_name(i, dir_prefix_h) for i in volume_names_input_h
                ]

            # grow volume-name lists
            volume_fullnames_input += volume_fullnames_input_h
            volume_names += volume_names_h

        volume_fullnames_input = np.array(volume_fullnames_input)
        volume_names = np.array(volume_names)
        lt = len(volume_names)

    # check timepoints
    parameters["type_timepoints"] = parameters["type_timepoints"].lower()
    if not parameters["type_timepoints"] in ["dff", "periodic", "custom"]:
        raise Exception("'type_timepoints' must be 'dff', 'periodic' or 'custom'.")
    else:
        print(
            "checking 'timepoints' for 'type_timepoints'='%s'."
            % parameters["type_timepoints"]
        )
        tp = parameters["timepoints"]
        if parameters["type_timepoints"] in ["dff", "periodic"]:
            if not (np.isscalar(tp) and (tp >= 0) and (tp == np.round(tp))):
                raise Exception("'timepoints' must be a nonnegative integer.")
            elif tp >= lt:
                warn(
                    "specified number of timepoints is greater than the number of volumes, overriding."
                )
                tp = 0
        elif parameters["type_timepoints"] in ["custom"]:
            tp = np.unique(tp)
            if not (
                (np.ndim(tp) == 1) and np.all(tp >= 0) and np.all(tp == np.round(tp))
            ):
                raise Exception(
                    "'timepoints' must be a one-dimensional vector of nonnegative integers."
                )
            elif np.any(tp >= lt):
                warn("discarding timepoints that exceed the number of volumes.")
                tp = tp[tp < lt]
            tp = tp.astype(int)

    # affine matrix
    affine_mat = np.diag(
        [
            parameters["res_x"] * parameters["ds"],
            parameters["res_y"] * parameters["ds"],
            parameters["res_z"],
            1,
        ]
    )

    # save parameters
    parameters["volume_fullnames_input"] = volume_fullnames_input
    parameters["volume_names"] = volume_names
    parameters["input_dirs"] = input_dirs
    parameters["ext"] = ext
    parameters["lt"] = lt
    parameters["affine_mat"] = affine_mat
    parameters["timepoints"] = tp

    try:
        os.makedirs(dir_output, exist_ok=True)
        with open(filename_parameters, "wb") as file_handle:
            pickle.dump(parameters, file_handle)
            print("parameter file successfully saved.")

    except Exception as msg:
        print("parameter file not saved: %s." % (msg))
