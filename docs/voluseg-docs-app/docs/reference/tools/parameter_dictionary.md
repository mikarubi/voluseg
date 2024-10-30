---
sidebar_label: parameter_dictionary
title: tools.parameter_dictionary
---

## Union

## ParametersModel

#### parameter\_dictionary

```python
def parameter_dictionary(detrending: str = "standard",
                         registration: str = "medium",
                         registration_restrict: str = "",
                         diam_cell: float = 6.0,
                         dir_ants: str = "",
                         dir_input: str = "",
                         dir_output: str = "",
                         dir_transform: str = "",
                         ds: int = 2,
                         planes_pad: int = 0,
                         planes_packed: bool = False,
                         parallel_clean: bool = True,
                         parallel_volume: bool = True,
                         save_volume: bool = False,
                         type_timepoints: str = "dff",
                         type_mask: str = "geomean",
                         timepoints: int = 1000,
                         f_hipass: float = 0,
                         f_volume: float = 2.0,
                         n_cells_block: int = 316,
                         n_colors: int = 1,
                         res_x: float = 0.40625,
                         res_y: float = 0.40625,
                         res_z: float = 5.0,
                         t_baseline: int = 300,
                         t_section: float = 0.01,
                         thr_mask: float = 0.5,
                         volume_fullnames_input: Union[list[str], None] = None,
                         volume_names: Union[list[str], None] = None,
                         input_dirs: Union[list[str], None] = None,
                         ext: Union[str, None] = None,
                         lt: Union[int, None] = None,
                         affine_matrix: Union[list, None] = None) -> dict
```

Return a parameter dictionary with specified defaults.

**Arguments**

* **detrending** (`str, optional`): Type of detrending: &#x27;standard&#x27;, &#x27;robust&#x27;, or &#x27;none&#x27; (default is &#x27;standard&#x27;).
* **registration** (`str, optional`): Quality of registration: &#x27;high&#x27;, &#x27;medium&#x27;, &#x27;low&#x27; or &#x27;none&#x27; (default is &#x27;medium&#x27;).
* **registration_restrict** (`str, optional`): Restrict registration (e.g. 1x1x1x1x1x1x0x0x0x1x1x0) (default is an empty string).
* **diam_cell** (`float, optional`): Cell diameter in microns (default is 6.0).
* **dir_ants** (`str, optional`): Path to the ANTs directory (default is an empty string).
* **dir_input** (`str, optional`): Path to input directories, separate multiple directories with &#x27;;&#x27; (default is an empty string).
* **dir_output** (`str, optional`): Path to the output directory (default is an empty string).
* **dir_transform** (`str, optional`): Path to the transform directory (default is an empty string).
* **ds** (`int, optional`): Spatial coarse-graining in x-y dimension (default is 2).
* **planes_pad** (`int, optional`): Number of planes to pad the volume with for robust registration (default is 0).
* **planes_packed** (`bool, optional`): Packed planes in each volume, for single plane imaging with packed planes (default is False).
* **parallel_clean** (`bool, optional`): Parallelization of final cleaning (True is fast but memory-intensive, default is True).
* **parallel_volume** (`bool, optional`): Parallelization of mean-volume computation (True is fast but memory-intensive, default is True).
* **save_volume** (`bool, optional`): Save registered volumes after segmentation, True keeps a copy of the volumes (default is False).
* **type_timepoints** (`str, optional`): Type of timepoints to use for cell detection: &#x27;dff&#x27;, &#x27;periodic&#x27; or &#x27;custom&#x27; (default is &#x27;dff&#x27;).
* **type_mask** (`str, optional`): Type of volume averaging for the mask: &#x27;mean&#x27;, &#x27;geomean&#x27; or &#x27;max&#x27; (default is &#x27;geomean&#x27;).
* **timepoints** (`int, optional`): Number (&#x27;dff&#x27;, &#x27;periodic&#x27;) or vector (&#x27;custom&#x27;) of timepoints for segmentation (default is 1000).
* **f_hipass** (`float, optional`): Frequency (Hz) for high-pass filtering of cell timeseries (default is 0).
* **f_volume** (`float, optional`): Imaging frequency in Hz (default is 2.0).
* **n_cells_block** (`int, optional`): Number of cells in a block. Small number is fast but can lead to blocky output (default is 316).
* **n_colors** (`int, optional`): Number of brain colors (2 in two-color volumes, default is 1).
* **res_x** (`float, optional`): X resolution in microns (default is 0.40625).
* **res_y** (`float, optional`): Y resolution in microns (default is 0.40625).
* **res_z** (`float, optional`): Z resolution in microns (default is 5.0).
* **t_baseline** (`int, optional`): Interval for baseline calculation in seconds (default is 300).
* **t_section** (`float, optional`): Exposure time in seconds for slice acquisition (default is 0.01).
* **thr_mask** (`float, optional`): Threshold for volume mask: 0 &lt; thr &lt;= 1 (probability) or thr &gt; 1 (intensity) (default is 0.5).
* **volume_fullnames_input** (`list[str], optional`): List of full volume names (default is None).
* **volume_names** (`list[str], optional`): List of volume names (default is None).
* **input_dirs** (`list[str], optional`): List of input directories (default is None).
* **ext** (`str, optional`): File extension (default is None).
* **lt** (`int, optional`): Number of volumes (default is None).
* **affine_matrix** (`list, optional`): Affine matrix (default is None).

**Returns**

* `dict`: A dictionary of validated parameters with their default values.

