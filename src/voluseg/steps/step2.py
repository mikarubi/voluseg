import os
import h5py
import shutil
import numpy as np
from scipy import io
from types import SimpleNamespace
from voluseg.tools.load_volume import load_volume
from voluseg.tools.save_volume import save_volume
from voluseg.tools.constants import ori, ali, nii, hdf, dtype
from voluseg.tools.ants_registration import ants_registration
from voluseg.tools.ants_transformation import ants_transformation
from voluseg.tools.evenly_parallelize import evenly_parallelize


def align_volumes(parameters: dict) -> None:
    """
    Register volumes to a reference volume.
    Generates ANTs transforms files (.mat).

    Parameters
    ----------
    parameters : dict
        Parameters dictionary.

    Returns
    -------
    None
    """
    # do not run if registration is set to none
    if not parameters["registration"]:
        return

    p = SimpleNamespace(**parameters)

    volume_nameRDD = evenly_parallelize(
        input_list=p.volume_names,
        parameters=parameters,
    )
    for color_i in range(p.n_colors):
        fullname_volmean = os.path.join(p.dir_output, "volume%d" % (color_i))
        if os.path.isfile(fullname_volmean + hdf):
            continue

        dir_volume = os.path.join(p.dir_output, "volumes", str(color_i))
        fullname_reference = os.path.join(dir_volume, "reference")
        if load_volume(fullname_reference + nii) is None:
            fullname_median = os.path.join(dir_volume, p.volume_names[p.lt // 2])
            shutil.copyfile(fullname_median + ori + nii, fullname_reference + nii)

        if p.dir_transform:
            dir_transform = os.path.join(p.dir_transform, str(color_i))
        else:
            dir_transform = os.path.join(p.dir_output, "transforms", str(color_i))
            os.makedirs(dir_transform, exist_ok=True)

        def get_fullname_tform(name_volume):
            return os.path.join(
                dir_transform, name_volume + "_tform_0GenericAffine.mat"
            )

        def load_transform(name_volume):
            try:
                tform = io.loadmat(get_fullname_tform(name_volume))
                tform_vector = tform[list(tform.keys())[0]].T[0]
                assert tform_vector.size == 12
                return tform_vector
            except:
                return np.full(12, np.nan)

        def register_volume(tuple_name_volume):
            import os

            # disable ITK multithreading
            os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "1"

            name_volume = tuple_name_volume[1]
            fullname_volume = os.path.join(dir_volume, name_volume)
            # skip processing if aligned volume exists
            if load_volume(fullname_volume + ali + hdf) is not None:
                tform_vector = load_transform(name_volume)
                return tform_vector

            # setup registration\
            if p.registration == "transform":
                cmd = ants_transformation(
                    dir_ants=p.dir_ants,
                    in_nii=fullname_volume + ori + nii,
                    ref_nii=fullname_reference + nii,
                    out_nii=fullname_volume + ali + nii,
                    in_tform=get_fullname_tform(name_volume),
                    interpolation="Linear",
                )
            else:
                cmd = ants_registration(
                    dir_ants=p.dir_ants,
                    in_nii=fullname_volume + ori + nii,
                    ref_nii=fullname_reference + nii,
                    out_nii=fullname_volume + ali + nii,
                    prefix_out_tform=os.path.join(
                        dir_transform, name_volume + "_tform_"
                    ),
                    restrict=p.registration_restrict,
                    typ="r",
                )
                if p.registration == "high":
                    pass
                elif p.registration == "medium":
                    cmd = (
                        cmd.replace("[1000x500x250x125]", "[1000x500x250]")
                        .replace("12x8x4x2", "12x8x4")
                        .replace("4x3x2x1vox", "4x3x2vox")
                    )
                elif p.registration == "low":
                    cmd = (
                        cmd.replace("[1000x500x250x125]", "[1000x500]")
                        .replace("12x8x4x2", "12x8")
                        .replace("4x3x2x1vox", "4x3vox")
                    )

            # run registration
            flag = os.system(cmd)
            if flag:
                # if breaks change initialization
                flag = os.system(cmd.replace(nii + ",1]", nii + ",0]"))
            if flag and load_volume(fullname_volume + ori + nii).shape[2] == 1:
                # if breaks change dimensionality
                flag = os.system(
                    cmd.replace("--dimensionality 3", "--dimensionality 2")
                )
                if not flag:
                    volume = load_volume(fullname_volume + ali + nii)[:, :, None]
                    save_volume(fullname_volume + ali + nii, volume, p.affine_matrix)
            if flag:
                raise Exception(
                    "volume %s not registered: flag %d." % (name_volume, flag)
                )

            # load aligned volume
            volume = load_volume(fullname_volume + ali + nii)

            # remove padding
            if p.planes_pad:
                volume = volume[:, :, p.planes_pad : -p.planes_pad]

            # save as hdf5
            volume = volume.T
            save_volume(fullname_volume + ali + hdf, volume)

            # remove nifti files
            if load_volume(fullname_volume + ali + hdf) is not None:
                try:
                    os.remove(fullname_volume + ori + nii)
                    os.remove(fullname_volume + ali + nii)
                except:
                    pass

            # return transform
            tform_vector = load_transform(name_volume)
            return tform_vector

        # run registration and save transforms as needed
        transforms = volume_nameRDD.map(register_volume).collect()
        if not p.registration == "transform":
            transforms = np.array(transforms).astype(dtype)
            fullname_tforms = os.path.join(dir_transform, "transforms%d" % (color_i))
            if not os.path.isfile(fullname_tforms + hdf):
                with h5py.File(fullname_tforms + hdf, "w") as file_handle:
                    file_handle["transforms"] = transforms
