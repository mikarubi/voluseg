def parameter_dictionary() -> dict:
    """
    Return parameter dictionary with specified defaults.

    Returns
    -------
    dict
        Parameters dictionary with default values.
    """

    return {
        "detrending": "standard",  # type of detrending: 'standard', 'robust', or 'none'
        "registration": "medium",  # quality of registration: 'high', 'medium', 'low' or 'none'
        "registration_restrict": "",  # restrict registration (e.g. 1x1x1x1x1x1x0x0x0x1x1x0)
        "diam_cell": 6.0,  # cell diameter (microns)
        "dir_ants": "",  # path to ANTs directory
        "dir_input": "",  # path to input directory/ies (separate multiple directories by ';')
        "dir_output": "",  # path to output directory
        "dir_transform": "",  # path to transform directory
        "ds": 2,  # spatial coarse-graining in x-y dimension
        "planes_pad": 0,  # number of planes to pad the volume with (for robust registration)
        "planes_packed": False,  # packed planes in each volume (for single plane imaging with packed planes)
        "parallel_clean": True,  # parallelization of final cleaning (True is fast but memory intensive)
        "parallel_volume": True,  # parallelization of mean-volume computation (True is fast but memory intensive)
        "save_volume": False,  # save registered volumes after segmentation (True keeps a copy of the volumes)
        "type_timepoints": "dff",  # type of timepoints to use for cell detection: 'dff', 'periodic' or 'custom'
        "type_mask": "geomean",  # type of volume averaging for mask: 'mean', 'geomean' or 'max'
        "timepoints": 1000,  # number ('dff'/'periodic') or vector ('custom') of timepoints for segmentation
        "f_hipass": 0,  # frequency (Hz) for high-pass filtering of cell timeseries
        "f_volume": 2.0,  # imaging frequency (Hz)
        "n_cells_block": 316,  # number of cells in block (small n_cells is fast but can lead to blocky output)
        "n_colors": 1,  # number of brain colors (2 in two-color volumes)
        "res_x": 0.40625,  # x resolution (microns)
        "res_y": 0.40625,  # y resolution (microns)
        "res_z": 5.0,  # z resolution (microns)
        "t_baseline": 300,  # interval for baseline calculation (seconds)
        "t_section": 0.01,  # exposure time (seconds): time of slice acquisition
        "thr_mask": 0.5,  # threshold for volume mask: 0 < thr <= 1 (probability) or thr > 1 (intensity)
    }
