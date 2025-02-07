import os
import copy
import json
import numpy as np
from warnings import warn
from voluseg._tools.load_volume import load_volume
from voluseg._tools.get_volume_name import get_volume_name
from voluseg._tools.parameter_dictionary import parameter_dictionary
from voluseg._tools.evenly_parallelize import evenly_parallelize
from voluseg._tools.parameters import load_parameters, save_parameters
from voluseg._tools.parameters_models import ParametersModel
from voluseg._tools.nwb import open_nwbfile, find_nwbfile_volume_object_name


def process_parameters(initial_parameters: dict) -> None:
    """
    Process parameters and create parameter file (pickle).

    Parameters
    ----------
    initial_parameters : dict
        Initial parameter dictionary
    """
    parameters = copy.deepcopy(initial_parameters)

    # check that parameter input is a dictionary
    if not isinstance(parameters, dict):
        raise Exception("specify parameter dictionary as input.")

    # check if any parameters are missing
    missing_parameters = set(parameter_dictionary()) - set(parameters)
    if missing_parameters:
        raise Exception("missing parameters '%s'." % ("', '".join(missing_parameters)))

    # get input directories
    dir_input = parameters["dir_input"]
    input_dirs = [os.path.normpath(h) for h in dir_input.split(";")]
    parameters["input_dirs"] = input_dirs

    # get output directory and parameter filename
    dir_output = parameters["dir_output"]
    filename_parameters = os.path.join(dir_output, "parameters.json")

    # load parameters from file, if it already exists
    if os.path.isfile(filename_parameters):
        print("Parameter file exists at: %s, aborting." % (filename_parameters))
        return None

    # check parameters file
    parameters = ParametersModel(**parameters).model_dump()

    # check plane padding
    if (parameters["registration"] == "none") and not ((parameters["planes_pad"] == 0)):
        raise Exception("'planes_pad' must be 0 if 'registration' is None.")

    # convert dir_input into a list to account for multiple directories
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

    remote = "https://" in dir_input
    volume_fullnames_input = []
    volume_names = []
    if (".nwb" in dir_input) or remote:
        if remote:
            aux_list = [dir_input]
        else:
            aux_list = dir_input.split(":")
        if len(input_dirs) > 1:
            raise Exception("Only one file path can be specified for NWB input.")
        volume_fullnames_input = [aux_list[0]]
        with open_nwbfile(
            input_path=volume_fullnames_input[0],
            remote=remote,
            output_path=dir_output,
        ) as nwbfile:
            if len(aux_list) == 2:
                volume_name = [aux_list[1]]
            else:
                volume_name = [find_nwbfile_volume_object_name(nwbfile)]
            lt = nwbfile.acquisition[volume_name[0]].data.shape[0]
            if parameters["timepoints"]:
                lt = min(lt, parameters["timepoints"])
        for ii in range(lt):
            volume_names.append(volume_name[0] + "_%d" % ii)
        ext = ".nwb"
        parameters["dim_order"] = "xyz"
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
            tp = lt
    elif parameters["type_timepoints"] in ["custom"]:
        tp = np.unique(tp)
        if not ((np.ndim(tp) == 1) and np.all(tp >= 0) and np.all(tp == np.round(tp))):
            raise Exception(
                "'timepoints' must be a one-dimensional vector of nonnegative integers."
            )
        elif np.any(tp >= lt):
            warn("discarding timepoints that exceed the number of volumes.")
            tp = tp[tp < lt]
        tp = tp.astype(int)

    # affine matrix
    affine_matrix = np.diag(
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
    parameters["affine_matrix"] = affine_matrix
    parameters["timepoints"] = tp
    parameters["remote"] = remote

    os.makedirs(dir_output, exist_ok=True)
    save_parameters(parameters=parameters, filename=filename_parameters)
