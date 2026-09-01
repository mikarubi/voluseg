import h5py
import nibabel
import numpy as np
import tifffile
from typing import Union

from voluseg._tools.constants import dtype


def load_volume(fullname_ext: str) -> Union[np.ndarray, None]:
    """
    Load volume based on input name and extension.
    Supports tiff, hdf5, and nifti formats.

    Parameters
    ----------
    fullname_ext : str
        Full name of volume with extension.

    Returns
    -------
    np.ndarray or None
        Volume as numpy array, or None if volume could not be loaded.
    """
    try:
        ext = "." + fullname_ext.split(".", 1)[1]
        if (".tif" in ext) or (".tiff" in ext):
            volume = tifffile.imread(fullname_ext)
        elif (".h5" in ext) or (".hdf5" in ext):
            with h5py.File(fullname_ext, "r") as file_handle:
                volume = file_handle[list(file_handle.keys())[0]][()]
        elif (".nii" in ext) or (".nii.gz" in ext):
            volume = nibabel.load(fullname_ext).get_fdata()
        else:
            raise Exception("unknown extension.")
        return volume.astype(dtype)

    except Exception:
        return None
