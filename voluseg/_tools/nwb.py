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
            file = h5py.File(f, 'r')
            io = pynwb.NWBHDF5IO(file=file, mode='r')
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
