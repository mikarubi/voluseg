import pynwb
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