from enum import Enum
import numpy as np
from pydantic import BaseModel, Field, model_validator
from typing import Optional


class Detrending(str, Enum):
    standard = "standard"
    robust = "robust"
    none = "none"


class Registration(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    none = "none"


class TypeTimepoints(str, Enum):
    dff = "dff"
    periodic = "periodic"
    custom = "custom"


class TypeMask(str, Enum):
    mean = "mean"
    geomean = "geomean"
    max = "max"


class ParametersModel(BaseModel):
    detrending: Detrending = Field(
        default=Detrending.standard,
        description="Type of detrending: 'standard', 'robust', or 'none'",
    )
    registration: Registration = Field(
        default=Registration.medium,
        description="Quality of registration: 'high', 'medium', 'low' or 'none'",
    )
    registration_restrict: Optional[str] = Field(
        default="",
        description="Restrict registration (e.g. 1x1x1x1x1x1x0x0x0x1x1x0)",
    )
    diam_cell: float = Field(
        default=6.0,
        description="Cell diameter in microns",
    )
    dir_ants: str = Field(
        default="",
        description="Path to ANTs directory",
    )
    dir_input: str = Field(
        default="",
        description="Path to input directory/ies (separate multiple directories by ';')",
    )
    dir_output: str = Field(
        default="",
        description="Path to output directory",
    )
    dir_transform: str = Field(
        default="",
        description="Path to transform directory",
    )
    ds: int = Field(
        default=2,
        description="Spatial coarse-graining in x-y dimension",
    )
    planes_pad: int = Field(
        default=0,
        description="Number of planes to pad the volume with for robust registration",
    )
    planes_packed: bool = Field(
        default=False,
        description="Packed planes in each volume (for single plane imaging with packed planes)",
    )
    parallel_clean: bool = Field(
        default=True,
        description="Parallelization of final cleaning (True is fast but memory intensive)",
    )
    parallel_volume: bool = Field(
        default=True,
        description="Parallelization of mean-volume computation (True is fast but memory intensive)",
    )
    save_volume: bool = Field(
        default=False,
        description="Save registered volumes after segmentation (True keeps a copy of the volumes)",
    )
    type_timepoints: TypeTimepoints = Field(
        default=TypeTimepoints.dff,
        description="Type of timepoints to use for cell detection: 'dff', 'periodic' or 'custom'",
    )
    type_mask: TypeMask = Field(
        default=TypeMask.geomean,
        description="Type of volume averaging for mask: 'mean', 'geomean' or 'max'",
    )
    timepoints: int = Field(
        default=1000,
        description="Number ('dff', 'periodic') or vector ('custom') of timepoints for segmentation",
    )
    f_hipass: float = Field(
        default=0,
        description="Frequency (Hz) for high-pass filtering of cell timeseries",
    )
    f_volume: float = Field(
        default=2.0,
        description="Imaging frequency in Hz",
    )
    n_cells_block: int = Field(
        default=316,
        description="Number of cells in a block. Small number is fast but can lead to blocky output",
    )
    n_colors: int = Field(
        default=1,
        description="Number of brain colors (2 in two-color volumes)",
    )
    res_x: float = Field(
        default=0.40625,
        description="X resolution in microns",
    )
    res_y: float = Field(
        default=0.40625,
        description="Y resolution in microns",
    )
    res_z: float = Field(
        default=5.0,
        description="Z resolution in microns",
    )
    t_baseline: int = Field(
        default=300,
        description="Interval for baseline calculation in seconds",
    )
    t_section: float = Field(
        default=0.01,
        description="Exposure time in seconds for slice acquisition",
    )
    thr_mask: float = Field(
        default=0.5,
        description="Threshold for volume mask: 0 < thr <= 1 (probability) or thr > 1 (intensity)",
    )
    volume_fullnames_input: Optional[list[str]] = Field(
        default=None,
        description="List of full volume names",
    )
    volume_names: Optional[list[str]] = Field(
        default=None,
        description="List of volume names",
    )
    input_dirs: Optional[list[str]] = Field(
        default=None,
        description="List of input directories",
    )
    ext: Optional[str] = Field(
        default=None,
        description="File extension",
    )
    lt: Optional[int] = Field(
        default=None,
        description="Number of volumes",
    )
    affine_matrix: Optional[list] = Field(
        default=None,
        description="Affine matrix",
    )
    dim_order: Optional[str] = Field(
        default="zyx",
        description="Dimensions order. Examples: 'zyx', 'xyz'",
    )

    @model_validator(mode="before")
    def convert_array_to_list(cls, values):
        """
        Validator to automatically convert NumPy arrays to lists.
        """
        for field, v in values.items():
            if isinstance(v, np.ndarray):
                values[field] = v.tolist()
        return values

    def model_dump(
        self,
        use_np_array: bool = True,
        *args,
        **kwargs,
    ):
        """
        Override the model_dump method to convert lists to NumPy arrays (if use_np_array is True)
        and Enums to their values.

        Parameters
        ----------
        use_np_array : bool, optional
            Convert lists to NumPy arrays (default is True)
        *args
            Positional arguments to pass to the parent class
        **kwargs
            Keyword arguments to pass to the parent class

        Returns
        -------
        dict
            A dictionary of the model's data
        """
        data = super().model_dump(*args, **kwargs)
        for key, value in data.items():
            if isinstance(value, list) and use_np_array:
                data[key] = np.array(value)
            if isinstance(value, Enum):
                data[key] = value.value
        return data
