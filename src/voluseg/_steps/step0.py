import os
import json
import numpy as np
from warnings import warn
from voluseg._tools.get_volume_name import get_volume_name
from voluseg._tools.parameters import save_parameters
from voluseg._tools.parameters_models import ParametersModel
from voluseg._tools.nwb import open_nwbfile, find_nwbfile_volume_object_name


def define_parameters(*, dir_input: str, dir_output: str, **kwargs) -> None:
    """
    Create and save a parameter dictionary with specified defaults.

    Required arguments:
        dir_input: Name of input directory/ies, separate multiple directories with ';'
        dir_output: Name of output directory (default is an empty string).

    Optional arguments:
        detrending: Type of detrending
            'standard', 'robust', or 'none' (default is 'standard').

        registration: Registration type or quality
            'high', 'medium', 'low', 'none' or 'transform' (default is 'medium').

        opts_ants: Dictionary of ANTs registration options

        diam_cell: Cell diameter in microns (default is 6.0).

        dir_transform: Path to the transform directory (required for 'transform' registration).

        nwb_output: Output in NWB format (default is False).

        ds: Spatial coarse-graining in x-y dimension (default is 2).

        planes_pad: Number of planes to pad the volume with for robust registration (default is 0).

        parallel_extra: Additional Parallelization that may be memory-intensive (default is True).

        save_volume: Save registered volumes after segmentation to check registration (default is False).

        type_mask: Type of volume averaging for the mask:
            'mean', 'geomean' or 'max' (default is 'geomean').

        type_timepoints: Type of timepoints to use for segmentation
            'dff', 'periodic' or 'custom' (default is 'dff').

        timepoints:
            Number of timepoints for segmenttaion (if type_timepoints is 'dff', 'periodic')
            Vector of timepoints for segmenttaion (if type_timepoints is 'custom')
            Default is 1000.

        f_hipass: Frequency (Hz) for high-pass filtering of cell timeseries (default is 0).

        f_volume: Imaging frequency in Hz (default is 2.0).

        n_cells_block: Number of cells in a segmentation block. (default is 316)
            Small number is fast but can lead to blocky output.

        Number of brain colors (default is 1). Use 2 in two-color volumes.

        res_x:  X resolution in microns (default is 0.40625).

        res_y:  Y resolution in microns (default is 0.40625).

        res_z:  Z resolution in microns (default is 5.0).

        t_baseline: Interval for baseline calculation in seconds (default is 300).

        t_section: Exposure time in seconds for slice acquisition (default is 0.01).

        thr_mask: Threshold for volume mask (default is 0.5).
            0 < thr <= 1 (probability threshold)
            thr > 1 (intensity threshold)

        overwrite: Overwrite existing parameter file (default is False).
    """

    # get input directories and output directory
    input_dirs = [os.path.normpath(h) for h in dir_input.split(";")]
    dir_output = os.path.normpath(dir_output)

    # check parameters, get json, and then convert to string
    parameters = ParametersModel(input_dirs=input_dirs, dir_output=dir_output, **kwargs)
    parameters = json.loads(parameters.model_dump_json())

    # check if parameter file exists and act accordingly
    filename_parameters = os.path.join(dir_output, "parameters.json")
    if os.path.isfile(filename_parameters):
        print("%s exists" % (filename_parameters), end=", ")
        if parameters["overwrite"]:
            print("overwriting.")
        else:
            print("aborting (set overwrite=True to overwrite).")
            return None
    del parameters["overwrite"]

    # process input directories
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

    # convert numpy arrays to lists for json compatibility
    for key, value in parameters.items():
        if isinstance(value, np.ndarray):
            parameters[key] = value.tolist()

    os.makedirs(dir_output, exist_ok=True)
    save_parameters(parameters=parameters, filename=filename_parameters)
