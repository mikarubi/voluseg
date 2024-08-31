import requests
import zipfile
import os
from pathlib import Path


def download_sample_data(destination_folder: str = ".") -> None:
    """
    Download sample data for Voluseg.

    Parameters
    ----------
    destination_folder : str, optional
        Folder where the sample data should be downloaded. If not provided, the data will be downloaded
        to the current working directory.

    Returns
    -------
    None
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

    else:
        print(f"Failed to download file. Status code: {response.status_code}")
