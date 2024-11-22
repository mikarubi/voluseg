import pynwb
from contextlib import contextmanager
from datetime import datetime
from dateutil.tz import tzlocal
from uuid import uuid4
import numpy as np


@contextmanager
def open_nwbfile_local(file_path: str):
    """
    Context manager to open and close a local NWB file.

    Parameters
    ----------
    file_path : str
        Path to NWB file.

    Yields
    ------
    pynwb.NWBFile
        The opened NWB file.
    """
    io = pynwb.NWBHDF5IO(file_path, "r")
    try:
        nwbfile = io.read()
        yield nwbfile
    finally:
        io.close()


@contextmanager
def open_nwbfile_remote(s3_url: str, output_path: str):
    """
    Context manager to open and close a remote NWB file.

    Parameters
    ----------
    s3_url : str
        S3 URL to NWB file.
    output_path : str
        Output path to cache the remote file.

    Yields
    ------
    pynwb.NWBFile
        The opened NWB file.
    """
    import fsspec
    import h5py
    from fsspec.implementations.cached import CachingFileSystem

    fs = fsspec.filesystem("http")
    fs = CachingFileSystem(
        fs=fs,
        cache_storage=output_path,
    )

    file = None
    io = None
    try:
        with fs.open(s3_url, "rb") as f:
            file = h5py.File(f, "r")
            io = pynwb.NWBHDF5IO(file=file, mode="r")
            nwbfile = io.read()
            yield nwbfile
    except Exception as e:
        print(f"Error occurred while accessing NWB file: {e}")
        raise e
    finally:
        if io:
            io.close()
        if file:
            file.close()


@contextmanager
def open_nwbfile(
    input_path: str,
    remote: bool,
    output_path: str = None,
):
    """
    Open and close an NWB file from either a local or remote source.

    Parameters
    ----------
    input_path : str
        Path to the NWB file. This can be a local file path or an S3 URL.
    remote : bool
        If True, the file is assumed to be remote (S3 URL), otherwise, it is assumed to be a local file.
    output_path : str
        Output path, only used to cache remote files.

    Yields
    ------
    pynwb.NWBFile
        The opened NWB file.
    """
    if remote:
        context_manager = open_nwbfile_remote(input_path, output_path)
    else:
        context_manager = open_nwbfile_local(input_path)

    with context_manager as nwbfile:
        yield nwbfile


def find_nwbfile_volume_object_name(nwbfile: pynwb.NWBFile) -> str:
    """
    Find the name of the `TwoPhotonSeries` volume object in the NWB file.

    Parameters
    ----------
    nwbfile : pynwb.NWBFile
        NWB file.

    Returns
    -------
    str
        Name of the volume object.
    """
    acquisition_names = [
        k
        for k in nwbfile.acquisition.keys()
        if nwbfile.acquisition[k].__class__.__name__ == "TwoPhotonSeries"
    ]
    if len(acquisition_names) != 1:
        raise ValueError(
            f"Expected 1 acquisition object, but found {len(acquisition_names)}"
        )
    return acquisition_names[0]


def get_nwbfile_volume(
    nwbfile: pynwb.NWBFile,
    acquisition_name: str = "TwoPhotonSeries",
) -> pynwb.NWBFile:
    """
    Get `TwoPhotonSeries` object from NWB file.

    Parameters
    ----------
    nwbfile : pynwb.NWBFile
        NWB file.
    acquisition_name : str (default: "TwoPhotonSeries")
        Acquisition name.

    Returns
    -------
    pynwb.NWBFile
        NWB file.
    """
    if acquisition_name not in nwbfile.acquisition:
        raise ValueError(
            f"Acquisition name '{acquisition_name}' not found in NWB file."
        )
    return nwbfile.acquisition[acquisition_name]


def write_nwbfile(
    output_path: str,
    cell_x: np.ndarray,
    cell_y: np.ndarray,
    cell_z: np.ndarray,
    cell_weights: np.ndarray,
    cell_timeseries: np.ndarray,
) -> None:
    """
    Write results to a local NWB file.

    Parameters
    ----------
    output_path : str
        Output path.
    cell_x : np.ndarray
        Voxel X coordinates for all cells.
    cell_y : np.ndarray
        Voxel Y coordinates for all cells.
    cell_z : np.ndarray
        Voxel Z coordinates for all cells.
    cell_weights : np.ndarray
        Voxel weights for all cells.
    cell_timeseries : np.ndarray
        Fluorescence timeseries data for all cells.

    Returns
    -------
    None
    """
    # Create NWB file basics
    nwbfile = pynwb.NWBFile(
        session_description="voluseg results",
        identifier=str(uuid4()),
        session_start_time=datetime.now(tzlocal()),  # TODO - get the correct metadata
    )
    device = nwbfile.create_device(name="Microscope")
    optical_channel = pynwb.ophys.OpticalChannel(
        name="OpticalChannel",
        description="an optical channel",
        emission_lambda=500.0,  # TODO - get the correct metadata
    )
    imaging_plane = nwbfile.create_imaging_plane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        description="Imaging plane",
        device=device,
        excitation_lambda=600.0,  # TODO - get the correct metadata
        indicator="GFP",  # TODO - get the correct metadata
        location="V1",  # TODO - get the correct metadata
        grid_spacing=[0.01, 0.01],  # TODO - get the correct metadata
        grid_spacing_unit="meters",  # TODO - get the correct metadata
    )

    # Create segmentation objects
    ophys_module = nwbfile.create_processing_module(
        name="ophys",
        description="optical physiology processed data",
    )
    img_seg = pynwb.ophys.ImageSegmentation()
    ophys_module.add(img_seg)
    ps = img_seg.create_plane_segmentation(
        name="PlaneSegmentation",
        description="output from voluseg",
        imaging_plane=imaging_plane,
    )
    n_cells = cell_weights.shape[0]
    for ci in range(0, n_cells):
        n_valid_voxels = len(np.where(cell_x[ci] != -1)[0])
        voxel_mask = np.array(
            (
                cell_x[ci][0:n_valid_voxels],
                cell_y[ci][0:n_valid_voxels],
                cell_z[ci][0:n_valid_voxels],
                cell_weights[ci][0:n_valid_voxels],
            )
        ).T
        ps.add_roi(voxel_mask=voxel_mask)

    # Create response series
    rt_region = ps.create_roi_table_region(
        region=list(range(0, n_cells)), description="ROIs table region"
    )
    roi_resp_series = pynwb.ophys.RoiResponseSeries(
        name="RoiResponseSeries",
        description="Fluorescence responses for ROIs",
        data=cell_timeseries.T,
        rois=rt_region,
        unit="lumens",  # TODO - get the correct metadata
        rate=1.0,  # TODO - get the correct metadata
    )
    fl = pynwb.ophys.Fluorescence(roi_response_series=roi_resp_series)
    ophys_module.add(fl)
    with pynwb.NWBHDF5IO(output_path, "w") as io:
        io.write(nwbfile)
