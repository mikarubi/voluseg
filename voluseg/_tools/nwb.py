import pynwb
import h5py
import numpy as np
from datetime import datetime
from uuid import uuid4
from dateutil import tz
from pathlib import Path
from contextlib import contextmanager


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
    io = pynwb.NWBHDF5IO(file_path, 'r')
    try:
        nwbfile = io.read()
        yield nwbfile
    finally:
        io.close()


def get_nwbfile_volume(
    nwbfile: pynwb.NWBFile,
    acquisition_name: str,
    volume_index: int,
) -> pynwb.NWBFile:
    """
    Get 3D volume from NWB file.

    Parameters
    ----------
    nwbfile : pynwb.NWBFile
        NWB file.
    acquisition_name : str
        Acquisition name.
    volume_index : int
        Volume index.

    Returns
    -------
    pynwb.NWBFile
        NWB file.
    """
    return nwbfile.acquisition[acquisition_name].data[volume_index]


def h5_dir_to_nwbfile(
    h5_dir: str,
    acquisition_name: str = "TwoPhotonSeries",
    max_volumes: int = None,
) -> pynwb.NWBFile:
    """
    Convert a directory of HDF5 files to a single NWB file.
    Each h5 file is assumed to contain a single volume.

    Parameters
    ----------
    h5_dir : str
        Directory of HDF5 files.
    acquisition_name : str
        Acquisition name.
    max_volumes : int
        Maximum number of volumes to read.

    Returns
    -------
    pynwb.NWBFile
        NWB file.
    """
    sorted_paths = sorted([str(p.resolve()) for p in Path(h5_dir).glob("*.h5")])
    datasets = []
    if max_volumes is None:
        max_volumes = len(sorted_paths)
    for p in sorted_paths[:max_volumes]:
        with h5py.File(p, 'r') as hdf:
            dataset = hdf['default'][:]
            datasets.append(dataset)
    concatenated_dataset = np.concatenate(datasets, axis=0)
    nwbfile = pynwb.NWBFile(
        session_description="description",
        identifier=str(uuid4()),
        session_start_time=datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific")),
    )
    device = nwbfile.create_device(
        name="Microscope",
        description="My two-photon microscope",
    )
    optical_channel = pynwb.ophys.OpticalChannel(
        name="OpticalChannel",
        description="an optical channel",
        emission_lambda=500.0,
    )
    imaging_plane = nwbfile.create_imaging_plane(
        name="ImagingPlane",
        optical_channel=optical_channel,
        description="a very interesting part of the brain",
        device=device,
        excitation_lambda=600.0,
        indicator="GFP",
        location="V1",
    )
    two_p_series = pynwb.ophys.TwoPhotonSeries(
        name=acquisition_name,
        description="Raw 2p data",
        data=concatenated_dataset,
        imaging_plane=imaging_plane,
        rate=1.0,
        unit="normalized amplitude",
    )
    nwbfile.add_acquisition(two_p_series)
    return nwbfile