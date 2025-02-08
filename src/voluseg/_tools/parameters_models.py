from enum import Enum
import numpy as np
from pydantic import BaseModel, Field, model_validator
from pydantic.types import (
    NonNegativeInt,
    NonNegativeFloat,
    PositiveInt,
    PositiveFloat,
    DirectoryPath,
)
from typing import List


class DimOrder(str, Enum):
    xyz = "xyz"
    xzy = "xzy"
    yxz = "yxz"
    yzx = "yzx"
    zxy = "zxy"
    zyx = "zyx"


class Detrending(str, Enum):
    standard = "standard"
    robust = "robust"
    none = "none"


class Registration(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    none = "none"
    transform = "transform"


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
        default=Detrending.standard.value,
        description="Type of detrending: 'standard', 'robust', or 'none'",
    )
    registration: Registration = Field(
        default=Registration.medium.value,
        description="Quality of registration: 'high', 'medium', 'low', 'none' or 'transform'",
    )
    registration_opts: dict = Field(
        default={},
        description="ANTs registration options",
    )
    diam_cell: PositiveFloat = Field(
        default=6.0,
        description="Cell diameter in microns",
    )
    input_dirs: List[DirectoryPath] = Field(
        description="Path to input directory/ies (separate multiple directories by ';')",
    )
    dir_output: DirectoryPath = Field(
        description="Path to output directory",
    )
    dir_transform: DirectoryPath = Field(
        description="Path to transform directory",
    )
    ds: PositiveInt = Field(
        default=2,
        description="Spatial coarse-graining in x-y dimension",
    )
    planes_pad: NonNegativeInt = Field(
        default=0,
        description="Number of planes to pad the volume with for robust registration",
    )
    parallel_extra: bool = Field(
        default=True,
        description="Additional parallelization (True is faster but memory intensive)",
    )
    save_volume: bool = Field(
        default=False,
        description="Save registered volumes after segmentation (True keeps a copy of the volumes)",
    )
    type_timepoints: TypeTimepoints = Field(
        default=TypeTimepoints.dff.value,
        description="Type of timepoints to use for cell detection: 'dff', 'periodic' or 'custom'",
    )
    type_mask: TypeMask = Field(
        default=TypeMask.geomean.value,
        description="Type of volume averaging for mask: 'mean', 'geomean' or 'max'",
    )
    f_hipass: NonNegativeFloat = Field(
        default=0,
        description="Frequency (Hz) for high-pass filtering of cell timeseries",
    )
    f_volume: PositiveFloat = Field(
        default=2.0,
        description="Imaging frequency in Hz",
    )
    n_cells_block: PositiveInt = Field(
        default=316,
        description="Number of cells in a block. Small number is fast but can lead to blocky output",
    )
    res_x: PositiveFloat = Field(
        default=0.40625,
        description="X resolution in microns",
    )
    res_y: PositiveFloat = Field(
        default=0.40625,
        description="Y resolution in microns",
    )
    res_z: PositiveFloat = Field(
        default=5.0,
        description="Z resolution in microns",
    )
    t_baseline: PositiveInt = Field(
        default=300,
        description="Interval for baseline calculation in seconds",
    )
    t_section: PositiveFloat = Field(
        default=0.01,
        description="Exposure time in seconds for slice acquisition",
    )
    thr_mask: NonNegativeFloat = Field(
        default=0.5,
        description="Threshold for volume mask: 0 < thr <= 1 (probability) or thr > 1 (intensity)",
    )
    dim_order: DimOrder = Field(
        default=DimOrder.zyx.value,
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

    class Config:
        extra = "allow"
