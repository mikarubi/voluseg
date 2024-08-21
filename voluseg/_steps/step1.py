import os
import numpy as np
from scipy import interpolate
from types import SimpleNamespace
from voluseg._tools.load_volume import load_volume
from voluseg._tools.save_volume import save_volume
from voluseg._tools.get_volume_name import get_volume_name
from voluseg._tools.constants import ori, ali, nii, hdf
from voluseg._tools.evenly_parallelize import evenly_parallelize


def process_volumes(parameters: dict) -> None:
    """
    Process original volumes and save into nifti format.
    Performs downsampling and padding if specified in parameters.

    Parameters
    ----------
    parameters : dict
        Parameters dictionary.

    Returns
    -------
    None
    """

    p = SimpleNamespace(**parameters)

    volume_fullname_inputRDD = evenly_parallelize(p.volume_fullnames_input)
    for color_i in range(p.n_colors):
        fullname_volmean = os.path.join(p.dir_output, "volume%d" % (color_i))
        if os.path.isfile(fullname_volmean + hdf):
            continue

        dir_volume = os.path.join(p.dir_output, "volumes", str(color_i))
        os.makedirs(dir_volume, exist_ok=True)

        def initial_processing(tuple_fullname_volume_input):

            def make_output_volume(name_volume, volume):
                # disable numpy multithreading
                os.environ["OMP_NUM_THREADS"] = "1"
                os.environ["MKL_NUM_THREADS"] = "1"
                os.environ["NUMEXPR_NUM_THREADS"] = "1"
                os.environ["OPENBLAS_NUM_THREADS"] = "1"
                os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

                # skip processing if output volume exists
                fullname_volume = os.path.join(dir_volume, name_volume)
                if (
                    load_volume(fullname_volume + ori + nii) is not None
                    or load_volume(fullname_volume + ali + hdf) is not None
                ):
                    return

                # fix dimensionality
                if volume.ndim == 2:
                    volume = volume[None, :, :]
                volume = volume.transpose(2, 1, 0)

                # get dimensions
                lx, ly, lz = volume.shape

                # split two-color volumes into two halves
                if p.n_colors == 2:
                    # ensure that two-frames have even number of y-dim voxels
                    assert ly % 2 == 0
                    ly //= 2
                    if color_i == 0:
                        volume = volume[:, :ly, :]
                    elif color_i == 1:
                        volume = volume[:, ly:, :]

                # downsample in the x-y if specified
                if p.ds > 1:
                    if (lx % p.ds) or (ly % p.ds):
                        lx -= lx % p.ds
                        ly -= ly % p.ds
                        volume = volume[:lx, :ly, :]

                    # make grid for computing downsampled values
                    sx_ds = np.arange(0.5, lx, p.ds)
                    sy_ds = np.arange(0.5, ly, p.ds)
                    xy_grid_ds = np.dstack(np.meshgrid(sx_ds, sy_ds, indexing="ij"))

                    # get downsampled volume
                    volume_ds = np.zeros((len(sx_ds), len(sy_ds), lz))
                    for zi in np.arange(lz):
                        interpolation_fx = interpolate.RegularGridInterpolator(
                            (np.arange(lx), np.arange(ly)),
                            volume[:, :, zi],
                            method="linear",
                        )
                        volume_ds[:, :, zi] = interpolation_fx(xy_grid_ds)

                    volume = volume_ds

                # pad planes as necessary
                if p.registration and p.planes_pad:
                    volume = np.lib.pad(
                        volume,
                        ((0, 0), (0, 0), (p.planes_pad, p.planes_pad)),
                        "constant",
                        constant_values=(np.percentile(volume, 1),),
                    )

                # save volume in output directory
                if p.registration:
                    save_volume(fullname_volume + ori + nii, volume, p.affine_mat)
                else:
                    volume = volume.T
                    save_volume(fullname_volume + ali + hdf, volume)

            # end make output volume

            # get full name of input volume, input data and list of planes
            fullname_volume_input = tuple_fullname_volume_input[1]
            volume = load_volume(fullname_volume_input + p.ext)
            if len(p.input_dirs) == 1:
                dir_prefix = None
            else:
                dir_prefix = os.path.basename(os.path.split(fullname_volume_input)[0])

            # process output volumes
            if p.planes_packed:
                for pi, volume_pi in enumerate(volume):
                    name_volume_pi = get_volume_name(
                        fullname_volume_input,
                        dir_prefix,
                        pi,
                    )
                    make_output_volume(name_volume_pi, volume_pi)
            else:
                name_volume = get_volume_name(fullname_volume_input, dir_prefix)
                make_output_volume(name_volume, volume)

        # end initial_processing

        volume_fullname_inputRDD.foreach(initial_processing)

        # except Exception as msg:
        #     raise Exception('volume %s not processed: %s.'%(name_volume, msg))
