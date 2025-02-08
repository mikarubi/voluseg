def parameter_dictionary(
    detrending="standard",
    registration="medium",
    registration_opts={},
    diam_cell=6.0,
    dim_order="zyx",
    dir_input="",
    dir_output="",
    dir_transform="",
    nwb_output=False,
    ds=2,
    planes_pad=0,
    parallel_extra=True,
    save_volume=False,
    type_timepoints="dff",
    type_mask="geomean",
    timepoints=1000,
    f_hipass=0,
    f_volume=2.0,
    n_cells_block=316,
    n_colors=1,
    res_x=0.40625,
    res_y=0.40625,
    res_z=5.0,
    t_baseline=300,
    t_section=0.01,
    thr_mask=0.5,
) -> dict:
    """
    Return a parameter dictionary with specified defaults.

    Parameters
    ----------
    detrending  = str, optional
        Type of detrending = 'standard', 'robust', or 'none' (default is 'standard').
    registration  = str, optional
        Quality of registration = 'high', 'medium', 'low' or 'none' (default is 'medium').
    registration_opts  = str, optional
        Restrict registration (e.g. 1x1x1x1x1x1x0x0x0x1x1x0) (default is an empty string).
    diam_cell  = float, optional
        Cell diameter in microns (default is 6.0).
    dir_ants  = str, optional
        Path to the ANTs directory (default is an empty string).
    dir_input  = str, optional
        Path to input directories, separate multiple directories with ';' (default is an empty string).
    dir_output  = str, optional
        Path to the output directory (default is an empty string).
    dir_transform  = str, optional
        Path to the transform directory (default is an empty string).
    ds  = int, optional
        Spatial coarse-graining in x-y dimension (default is 2).
    planes_pad  = int, optional
        Number of planes to pad the volume with for robust registration (default is 0).
    parallel_extra  = bool, optional
        Additional Parallelization (True is fast but more memory-intensive, default is True).
    save_volume  = bool, optional
        Save registered volumes after segmentation, True keeps a copy of the volumes (default is False).
    type_timepoints  = str, optional
        Type of timepoints to use for cell detection = 'dff', 'periodic' or 'custom' (default is 'dff').
    type_mask  = str, optional
        Type of volume averaging for the mask = 'mean', 'geomean' or 'max' (default is 'geomean').
    timepoints  = int, optional
        Number ('dff', 'periodic') or vector ('custom') of timepoints for segmentation (default is 1000).
    f_hipass  = float, optional
        Frequency (Hz) for high-pass filtering of cell timeseries (default is 0).
    f_volume  = float, optional
        Imaging frequency in Hz (default is 2.0).
    n_cells_block  = int, optional
        Number of cells in a block. Small number is fast but can lead to blocky output (default is 316).
    n_colors  = int, optional
        Number of brain colors (2 in two-color volumes, default is 1).
    res_x  = float, optional
        X resolution in microns (default is 0.40625).
    res_y  = float, optional
        Y resolution in microns (default is 0.40625).
    res_z  = float, optional
        Z resolution in microns (default is 5.0).
    t_baseline  = int, optional
        Interval for baseline calculation in seconds (default is 300).
    t_section  = float, optional
        Exposure time in seconds for slice acquisition (default is 0.01).
    thr_mask  = float, optional
        Threshold for volume mask = 0 < thr <= 1 (probability) or thr > 1 (intensity) (default is 0.5).
    volume_fullnames_input  = list[str], optional
        List of full volume names (default is None).
    volume_names  = list[str], optional
        List of volume names (default is None).
    input_dirs  = list[str], optional
        List of input directories (default is None).
    ext  = str, optional
        File extension (default is None).
    lt  = int, optional
        Number of volumes (default is None).
    affine_matrix  = list, optional
        Affine matrix (default is None).

    Returns
    -------
    dict
        A dictionary of validated parameters with their default values.
    """
    # Return parameters
    parameters = {key: value for key, value in locals().items()}
    return parameters
