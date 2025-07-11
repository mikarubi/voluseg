---
sidebar_label: step0
title: _steps.step0
---

#### define\_parameters

```python
def define_parameters(*, dir_input: str, dir_output: str, **kwargs) -> str
```

Create and save a parameter dictionary with specified defaults.

Required arguments:
    dir_input: Name of input directory/ies, separate multiple directories with &#x27;;&#x27;
    dir_output: Name of output directory (default is an empty string).

Optional arguments:
    detrending: Type of detrending
        &#x27;standard&#x27;, &#x27;robust&#x27;, or &#x27;none&#x27; (default is &#x27;standard&#x27;).

    registration: Registration type or quality
        &#x27;high&#x27;, &#x27;medium&#x27;, &#x27;low&#x27;, &#x27;none&#x27; or &#x27;transform&#x27; (default is &#x27;medium&#x27;).

    opts_ants: Dictionary of ANTs registration options

    diam_cell: Cell diameter in microns (default is 6.0).

    dir_transform: Path to the transform directory (required for &#x27;transform&#x27; registration).

    nwb_output: Output in NWB format (default is False).

    ds: Spatial coarse-graining in x-y dimension (default is 2).

    planes_pad: Number of planes to pad the volume with for robust registration (default is 0).

    parallel_extra: Additional Parallelization that may be memory-intensive (default is True).

    save_volume: Save registered volumes after segmentation to check registration (default is False).

    type_mask: Type of volume averaging for the mask:
        &#x27;mean&#x27;, &#x27;geomean&#x27; or &#x27;max&#x27; (default is &#x27;geomean&#x27;).

    type_timepoints: Type of timepoints to use for segmentation
        &#x27;dff&#x27;, &#x27;periodic&#x27; or &#x27;custom&#x27; (default is &#x27;dff&#x27;).

    timepoints:
        Number of timepoints for segmenttaion (if type_timepoints is &#x27;dff&#x27;, &#x27;periodic&#x27;)
        Vector of timepoints for segmenttaion (if type_timepoints is &#x27;custom&#x27;)
        Default is 1000.

    f_hipass: Frequency (Hz) for high-pass filtering of cell timeseries (default is 0).

    f_volume: Imaging frequency in Hz (default is 2.0).

    n_cells_block: Number of cells in a segmentation block. (default is 316)
        Small number is fast but can lead to blocky output.

    n_colors: Number of brain colors (default is 1). Use 2 in two-color volumes.

    res_x:  X resolution in microns (default is 0.40625).

    res_y:  Y resolution in microns (default is 0.40625).

    res_z:  Z resolution in microns (default is 5.0).

    t_baseline: Interval for baseline calculation in seconds (default is 300).

    t_section: Exposure time in seconds for slice acquisition (default is 0.01).

    thr_mask: Threshold for volume mask (default is 0.5).
        0 &lt; thr &lt;= 1 (probability threshold)
        thr &gt; 1 (intensity threshold)

    overwrite: Overwrite existing parameter file (default is False).

