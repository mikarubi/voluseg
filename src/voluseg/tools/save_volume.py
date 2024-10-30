import h5py
import nibabel
import numpy as np
from typing import Union
from voluseg.tools.constants import dtype


def save_volume(
    fullname_ext: str,
    volume: np.ndarray,
    affine_matrix: np.ndarray = None,
) -> Union[bool, None]:
    """
    Save volume in output format.
    Formats currently accepted are: nifti and hdf5.

    Parameters
    ----------
    fullname_ext : str
        Full name of volume with extension.
    volume : np.ndarray
        Volume as numpy array.
    affine_matrix : np.ndarray
        Affine matrix for nifti format.

    Returns
    -------
    bool or None
        True if volume was saved successfully, None if volume could not be saved.
    """
    try:
        volume = volume.astype(dtype)
        ext = "." + fullname_ext.split(".", 1)[1]

        if (".h5" in ext) or (".hdf5" in ext):
            with h5py.File(fullname_ext, "w") as file_handle:
                file_handle.create_dataset("volume", data=volume, compression="gzip")
        elif (".nii" in ext) or (".nii.gz" in ext):
            nii = nibabel.Nifti1Image(volume, affine_matrix)
            nii.header["qform_code"] = 2  # make codes consistent with ANTS
            nii.header["sform_code"] = 1  # 1 scanner, 2 aligned, 3 tlrc, 4 mni.
            nibabel.save(nii, fullname_ext)
        else:
            raise Exception("unknown extension.")

        return True

    except:
        return None
