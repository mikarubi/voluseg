import requests
import zipfile
import os
from pathlib import Path
from typing import Union


def download_sample_data(
    destination_folder: str = ".",
    data_type: str = "h5_dir",
) -> Union[str, None]:
    """
    Download sample data for Voluseg.

    Parameters
    ----------
    destination_folder : str, optional
        Folder where the sample data should be downloaded. If not provided, the data will be downloaded
        to the current working directory.
    data_type : str, optional
        Type of data to download. Options are "h5_dir" and "nwb_file".

    Returns
    -------
    str or None
        Path to the folder or file where the data was downloaded, or None if the download failed.
    """
    if data_type == "h5_dir":
        return download_sample_data_h5_dir(destination_folder)
    elif data_type == "nwb_file":
        return download_sample_data_nwb_file(destination_folder)
    else:
        print(f"Invalid data type: {data_type}")
        return None


def download_sample_data_nwb_file(destination_folder: str = ".") -> Union[str, None]:
    """
    Download sample NWB file for Voluseg.
    Ref: https://gui-staging.dandiarchive.org/dandiset/215495/draft

    Parameters
    ----------
    destination_folder : str, optional
        Folder where the sample data should be downloaded. If not provided, the data will be downloaded
        to the current working directory.

    Returns
    -------
    str or None
        Path to the downloaded file, or None if the download failed.
    """
    from dandi.dandiapi import DandiAPIClient

    dandiset_id = "215495"
    nwb_file_path = "sub-001/sub-001_ophys.nwb"

    with DandiAPIClient.for_dandi_instance("dandi-staging") as client:
        dandiset = client.get_dandiset(dandiset_id)
        asset = dandiset.get_asset_by_path(nwb_file_path)
        s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)

    response = requests.get(s3_url, stream=True)
    if response.status_code == 200:
        output_file = Path(destination_folder) / "downloaded.nwb"
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"File downloaded successfully as {output_file}")
        return str(output_file)
    else:
        print(f"Failed to download NWB file. Status code: {response.status_code}")
        return None


def download_sample_data_h5_dir(destination_folder: str = ".") -> Union[str, None]:
    """
    Download sample data (h5 directory) for Voluseg.

    Parameters
    ----------
    destination_folder : str, optional
        Folder where the sample data should be downloaded. If not provided, the data will be downloaded
        to the current working directory.

    Returns
    -------
    str or None
        Path to the folder where the data was extracted, or None if the download failed.
    """
    # Download the ZIP file
    download_url = "https://drive.usercontent.google.com/download"
    params = {
        "id": "1d_D_OAPIwUIzBFCghrBbDOMMLIaeHlQB",
        "export": "download",
        "authuser": "0",
        "confirm": "t",
    }
    response = requests.get(download_url, params=params, stream=True)
    if response.status_code == 200:
        destination_folder = str(Path(destination_folder).resolve())
        os.makedirs(destination_folder, exist_ok=True)
        filename = str(Path(destination_folder) / "downloaded_data.zip")
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully as {filename}")

        # Extract the contents of the ZIP file
        extract_folder = str(Path(destination_folder) / "downloaded_data")
        os.makedirs(extract_folder, exist_ok=True)

        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(extract_folder)
        print(f"Contents extracted to folder: {extract_folder}")

        # Remove the ZIP file
        os.remove(filename)
        print(f"Removed the ZIP file: {filename}")
        return extract_folder
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return None
