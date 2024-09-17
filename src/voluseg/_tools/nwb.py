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
    io = pynwb.NWBHDF5IO(file_path, "r")
    try:
        nwbfile = io.read()
        yield nwbfile
    finally:
        io.close()


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
