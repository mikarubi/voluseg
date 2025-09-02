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
from typing import List, Union


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
    input_dirs: List[str]
    dir_output: str
    dir_transform: DirectoryPath = Field(default="")
    detrending: Detrending = Field(default=Detrending.standard)
    registration: Registration = Field(default=Registration.medium)
    opts_ants: dict = Field(default={})
    diam_cell: PositiveFloat = Field(default=6.0)
    dim_order: DimOrder = Field(default=DimOrder.zyx)
    nwb_output: bool = Field(default=False)
    ds: PositiveInt = Field(default=2)
    planes_pad: NonNegativeInt = Field(default=0)
    parallel_extra: bool = Field(default=True)
    save_volume: bool = Field(default=False)
    type_timepoints: TypeTimepoints = Field(default=TypeTimepoints.dff)
    timepoints: Union[NonNegativeInt, List[NonNegativeInt]] = Field(default=1000)
    type_mask: TypeMask = Field(default=TypeMask.geomean)
    f_hipass: NonNegativeFloat = Field(default=0)
    f_volume: PositiveFloat = Field(default=2.0)
    n_cells_block: PositiveInt = Field(default=316)
    n_colors: PositiveInt = Field(default=1)
    res_x: PositiveFloat = Field(default=0.40625)
    res_y: PositiveFloat = Field(default=0.40625)
    res_z: PositiveFloat = Field(default=5.0)
    t_baseline: PositiveInt = Field(default=300)
    t_section: PositiveFloat = Field(default=0.01)
    thr_mask: NonNegativeFloat = Field(default=0.5)
    overwrite: bool = Field(default=False)

    @model_validator(mode="before")
    def convert_array_to_list(cls, values):
        """
        Validator to automatically convert NumPy arrays to lists.
        """
        for field, v in values.items():
            if isinstance(v, np.ndarray):
                values[field] = v.tolist()
        return values
