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
        raise ValueError(f"Acquisition name '{acquisition_name}' not found in NWB file.")
    return nwbfile.acquisition[acquisition_name]