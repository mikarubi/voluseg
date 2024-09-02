from enum import Enum
from pydantic import BaseModel, Field
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

    class Config:
        use_enum_values = True  # Automatically use the string values of Enums
