---
sidebar_label: sample_data
title: tools.sample_data
---

## requests

## zipfile

## os

## Path

## Union

#### download\_sample\_data

```python
def download_sample_data(destination_folder: str = ".",
                         data_type: str = "h5_dir") -> Union[str, None]
```

Download sample data for Voluseg.

**Arguments**

* **destination_folder** (`str, optional`): Folder where the sample data should be downloaded. If not provided, the data will be downloaded
to the current working directory.
* **data_type** (`str, optional`): Type of data to download. Options are &quot;h5_dir&quot; and &quot;nwb_file&quot;.

**Returns**

* `str or None`: Path to the folder or file where the data was downloaded, or None if the download failed.

#### download\_sample\_data\_nwb\_file

```python
def download_sample_data_nwb_file(
        destination_folder: str = ".") -> Union[str, None]
```

Download sample NWB file for Voluseg.
Ref: https://gui-staging.dandiarchive.org/dandiset/215495/draft

**Arguments**

* **destination_folder** (`str, optional`): Folder where the sample data should be downloaded. If not provided, the data will be downloaded
to the current working directory.

**Returns**

* `str or None`: Path to the downloaded file, or None if the download failed.

#### download\_sample\_data\_h5\_dir

```python
def download_sample_data_h5_dir(
        destination_folder: str = ".") -> Union[str, None]
```

Download sample data (h5 directory) for Voluseg.

**Arguments**

* **destination_folder** (`str, optional`): Folder where the sample data should be downloaded. If not provided, the data will be downloaded
to the current working directory.

**Returns**

* `str or None`: Path to the folder where the data was extracted, or None if the download failed.

